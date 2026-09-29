import json
from typing import Any

from app.llm.base import LLMClient
from app.llm.exceptions import LLMRequestError
from app.llm.types import (
    ChatCompletionRequest,
    ChatMessage,
    ToolCall,
)
from app.schemas import InvestigationQueryResponse, ToolExecutionStep
from app.services.investigation_workflow import build_investigation_response
from app.services.rca import generate_structured_rca
from app.tools.definitions import PAYMENT_INVESTIGATION_TOOLS
from app.tools.executor import PaymentToolExecutor, parse_tool_arguments
from app.tools.exceptions import ToolError

INVESTIGATION_SYSTEM_PROMPT = """You are FinPilot, a payment investigation assistant.

Gather evidence using the available tools before the RCA step runs.
You have four tools: get_payment, get_payment_events, search_logs, and search_payment_docs.

Workflow:
1. Confirm payment details with get_payment.
2. Review lifecycle with get_payment_events when the failure path is unclear.
3. Search logs for gateway responses, errors, and timeouts.
4. Search internal documentation for error codes, retry policy, and gateway guidance.

Only call tools you need, but ensure you have enough evidence for a root-cause analysis.
Do not invent payment data. Do not produce the final RCA JSON yourself."""


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
        messages: list[ChatMessage] = [
            ChatMessage(role="system", content=INVESTIGATION_SYSTEM_PROMPT),
            ChatMessage(
                role="user",
                content=(
                    f"Payment ID: {payment_id}\n"
                    f"Question: {question}\n"
                    "Use tools to gather payment facts, events, logs, and documentation."
                ),
            ),
        ]
        steps = self._run_tool_gathering_phase(messages)
        rca, model, provider = generate_structured_rca(
            self._llm,
            messages,
            payment_id=payment_id,
            question=question,
        )
        return build_investigation_response(
            payment_id=payment_id,
            question=question,
            steps=steps,
            rca=rca,
            model=model,
            provider=provider,
        )

    def _run_tool_gathering_phase(self, messages: list[ChatMessage]) -> list[ToolExecutionStep]:
        steps: list[ToolExecutionStep] = []

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
                steps.append(step)
                messages.append(
                    ChatMessage(
                        role="tool",
                        content=json.dumps(step.result),
                        tool_call_id=tool_call.id,
                        name=tool_call.name,
                    )
                )

        return steps

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
