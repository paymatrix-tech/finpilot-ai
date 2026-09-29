from app.llm.base import LLMClient
from app.llm.exceptions import LLMRequestError
from app.llm.types import (
    AssistantMessage,
    ChatCompletionRequest,
    ChatCompletionResponse,
)


class StubLLMClient(LLMClient):
    """Deterministic client for local development and tests without an API key."""

    def __init__(self, model: str = "stub") -> None:
        self._model = model

    @property
    def provider(self) -> str:
        return "stub"

    def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        if not request.messages:
            raise LLMRequestError("At least one message is required.")

        if request.tools:
            raise LLMRequestError("Stub LLM does not support tool calling.")

        last_user = next(
            (message.content for message in reversed(request.messages) if message.role == "user"),
            None,
        )
        if last_user is None:
            last_user = request.messages[-1].content or ""

        return ChatCompletionResponse(
            message=AssistantMessage(content=f"Stub response: {last_user}"),
            model=self._model,
            provider=self.provider,
        )
