import json
from collections.abc import Iterator
from typing import Any

from app.llm.base import LLMClient
from app.llm.exceptions import LLMRequestError
from app.llm.types import (
    ChatCompletionRequest,
    ChatMessage,
    ToolCall,
)
from app.prompts.investigation import INVESTIGATION_SYSTEM_PROMPT
from app.schemas import InvestigationQueryResponse, ToolExecutionStep
from app.services.evidence_requirements import apply_evidence_requirements
from app.services.investigation_workflow import build_investigation_response
from app.services.rca import generate_structured_rca
from app.tools.definitions import PAYMENT_INVESTIGATION_TOOLS
from app.tools.executor import PaymentToolExecutor, parse_tool_arguments
from app.tools.exceptions import ToolError

InvestigationEvent = tuple[str, dict[str, Any]]


class InvestigationAgent:
    def __init__(
        self,
        llm: LLMClient,
        tool_executor: PaymentToolExecutor,
        *,
        max_tool_rounds: int = 6,
    ) -> None:
        self._llm = llm
        self._tool_executor = tool_executor
        self._max_tool_rounds = max_tool_rounds

    def investigate(self, payment_id: str, question: str) -> InvestigationQueryResponse:
        for event, payload in self.investigate_with_events(payment_id, question):
            if event == "complete":
                return InvestigationQueryResponse.model_validate(payload)
        raise LLMRequestError("Investigation finished without a result.")

    def investigate_with_events(
        self,
        payment_id: str,
        question: str,
    ) -> Iterator[InvestigationEvent]:
        yield "started", {"payment_id": payment_id, "question": question}

        messages: list[ChatMessage] = [
            ChatMessage(role="system", content=INVESTIGATION_SYSTEM_PROMPT),
            ChatMessage(
                role="user",
                content=(
                    f"Payment ID: {payment_id}\n"
                    f"Question: {question}\n"
                    "Investigate using tools. Collect observed facts for a later RCA "
                    "(payment record, events, logs, and docs as needed)."
                ),
            ),
        ]
        steps: list[ToolExecutionStep] = []
        for step in self._iter_tool_gathering_steps(messages):
            steps.append(step)
            yield "tool_step", step.model_dump(mode="json")

        yield "rca_started", {}
        rca, model, provider = generate_structured_rca(
            self._llm,
            messages,
            payment_id=payment_id,
            question=question,
        )
        rca = apply_evidence_requirements(rca, steps=steps)
        response = build_investigation_response(
            payment_id=payment_id,
            question=question,
            steps=steps,
            rca=rca,
            model=model,
            provider=provider,
        )
        yield "complete", json.loads(response.model_dump_json())

    def _iter_tool_gathering_steps(
        self,
        messages: list[ChatMessage],
    ) -> Iterator[ToolExecutionStep]:
        for _ in range(self._max_tool_rounds):
            response = self._llm.chat_completion(
                ChatCompletionRequest(
                    messages=messages,
                    tools=PAYMENT_INVESTIGATION_TOOLS,
                )
            )
            assistant = response.message

            if not assistant.tool_calls:
                if assistant.content:
                    messages.append(
                        ChatMessage(role="assistant", content=assistant.content),
                    )
                break

            messages.append(
                ChatMessage(
                    role="assistant",
                    content=assistant.content,
                    tool_calls=assistant.tool_calls,
                )
            )
            for tool_call in assistant.tool_calls:
                step = self._run_tool(tool_call)
                yield step
                messages.append(
                    ChatMessage(
                        role="tool",
                        content=json.dumps(step.result),
                        tool_call_id=tool_call.id,
                        name=tool_call.name,
                    )
                )

    def _run_tool(self, tool_call: ToolCall) -> ToolExecutionStep:
        try:
            arguments = parse_tool_arguments(tool_call.arguments)
        except ToolError as exc:
            result: Any = {"error": "invalid_arguments", "message": str(exc)}
            return ToolExecutionStep(tool=tool_call.name, arguments={}, result=result)

        try:
            result = self._tool_executor.execute(tool_call.name, arguments)
        except ToolError as exc:
            result = {"error": "tool_error", "message": str(exc)}

        return ToolExecutionStep(tool=tool_call.name, arguments=arguments, result=result)
