import json
import re

from app.llm.base import LLMClient
from app.llm.exceptions import LLMRequestError
from app.llm.types import (
    AssistantMessage,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ToolCall,
)
from app.prompts.investigation import RCA_JSON_MARKER


class StubLLMClient(LLMClient):
    """Deterministic client for local development and tests without an API key."""

    def __init__(self, model: str = "stub") -> None:
        self._model = model
        self._gathering_turns = 0

    @property
    def provider(self) -> str:
        return "stub"

    def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        if not request.messages:
            raise LLMRequestError("At least one message is required.")

        if request.tools:
            return self._gather_tool_evidence(request)

        last_user = next(
            (message.content for message in reversed(request.messages) if message.role == "user"),
            None,
        )
        if last_user is None:
            last_user = request.messages[-1].content or ""

        if RCA_JSON_MARKER in last_user:
            return ChatCompletionResponse(
                message=AssistantMessage(content=json.dumps(_stub_rca_payload(request.messages))),
                model=self._model,
                provider=self.provider,
            )

        return ChatCompletionResponse(
            message=AssistantMessage(content=f"Stub response: {last_user}"),
            model=self._model,
            provider=self.provider,
        )

    def _gather_tool_evidence(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        self._gathering_turns += 1
        payment_id = _find_payment_id(request.messages)
        if self._gathering_turns == 1 and payment_id:
            return ChatCompletionResponse(
                message=AssistantMessage(
                    content=None,
                    tool_calls=[
                        ToolCall(
                            id="stub-call-payment",
                            name="get_payment",
                            arguments=json.dumps({"payment_id": payment_id}),
                        )
                    ],
                ),
                model=self._model,
                provider=self.provider,
            )

        return ChatCompletionResponse(
            message=AssistantMessage(content="Stub evidence gathering complete."),
            model=self._model,
            provider=self.provider,
        )


def _find_payment_id(messages) -> str | None:
    pattern = re.compile(r"PAY-[A-Z0-9-]+")
    for message in reversed(messages):
        if not message.content:
            continue
        match = pattern.search(message.content)
        if match:
            return match.group(0)
    return None


def _stub_rca_payload(messages) -> dict[str, object]:
    tool_payload = " ".join(
        message.content or ""
        for message in messages
        if message.role == "tool"
    )
    root_cause = "Insufficient evidence to determine the root cause."
    recommendation = "Gather more payment, log, and documentation evidence."
    evidence = ["Stub investigation completed without live model output."]
    sources: list[str] = []
    confidence = "low"

    if "R01" in tool_payload:
        root_cause = "Insufficient funds"
        recommendation = "Do not retry immediately; notify the customer to fund the account."
        evidence = [
            "Gateway returned error code R01",
            "Payment status is FAILED",
        ]
        sources = ["ach-error-codes.md"]
        confidence = "high"
    elif "TIMEOUT" in tool_payload:
        root_cause = "Gateway timeout"
        recommendation = "Retry with exponential backoff per retry policy."
        evidence = ["Gateway request timed out before a response was received"]
        sources = ["retry-policy.md", "timeout-handling.md"]
        confidence = "medium"

    return {
        "root_cause": root_cause,
        "confidence": confidence,
        "evidence": evidence,
        "recommendation": recommendation,
        "sources": sources,
    }
