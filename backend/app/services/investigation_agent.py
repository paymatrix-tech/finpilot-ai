import json
from typing import Any

from app.llm.base import LLMClient
from app.llm.exceptions import LLMRequestError
from app.llm.types import (
    AssistantMessage,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
    ToolCall,
)
from app.schemas import InvestigationQueryResponse, ToolExecutionStep
from app.tools.definitions import PAYMENT_INVESTIGATION_TOOLS
from app.tools.executor import PaymentToolExecutor, parse_tool_arguments
from app.tools.exceptions import ToolError

SYSTEM_PROMPT = """You are FinPilot, a payment investigation assistant.

Use the available tools to gather facts about the payment before answering.
Only state facts supported by tool results. If evidence is insufficient, say so clearly.
When the user asks about a specific payment, call tools as needed rather than guessing.
Use search_payment_docs for retry policy, error code meaning, and gateway runbook guidance.
Cite documentation sources when you rely on them."""


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
            ChatMessage(role="system", content=SYSTEM_PROMPT),
            ChatMessage(
                role="user",
                content=(
                    f"Payment ID: {payment_id}\n"
                    f"Question: {question}\n"
                    "Use tools when you need payment data, events, logs, or internal documentation."
                ),
            ),
        ]
        steps: list[ToolExecutionStep] = []
        model = ""
        provider = self._llm.provider

        for _ in range(self._max_tool_rounds):
            response = self._llm.chat_completion(
                ChatCompletionRequest(
                    messages=messages,
                    tools=PAYMENT_INVESTIGATION_TOOLS,
                )
            )
            model = response.model
            provider = response.provider
            assistant = response.message

            if assistant.tool_calls:
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
                continue

            if assistant.content and assistant.content.strip():
                return InvestigationQueryResponse(
                    answer=assistant.content.strip(),
                    steps=steps,
                    model=model,
                    provider=provider,
                )

            raise LLMRequestError("Model returned an empty response without tool calls.")

        raise LLMRequestError(
            f"Investigation exceeded the maximum of {self._max_tool_rounds} tool rounds."
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
