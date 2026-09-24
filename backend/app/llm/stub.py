from app.llm.base import LLMClient
from app.llm.exceptions import LLMRequestError
from app.llm.types import ChatCompletionRequest, ChatCompletionResult


class StubLLMClient(LLMClient):
    """Deterministic client for local development and tests without an API key."""

    def __init__(self, model: str = "stub") -> None:
        self._model = model

    @property
    def provider(self) -> str:
        return "stub"

    def complete(self, request: ChatCompletionRequest) -> ChatCompletionResult:
        if not request.messages:
            raise LLMRequestError("At least one message is required.")

        last_user = next(
            (message.content for message in reversed(request.messages) if message.role == "user"),
            None,
        )
        if last_user is None:
            last_user = request.messages[-1].content

        return ChatCompletionResult(
            content=f"Stub response: {last_user}",
            model=self._model,
            provider=self.provider,
        )
