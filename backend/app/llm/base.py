from abc import ABC, abstractmethod

from app.llm.exceptions import LLMRequestError
from app.llm.types import ChatCompletionRequest, ChatCompletionResponse, ChatCompletionResult


class LLMClient(ABC):
    @property
    @abstractmethod
    def provider(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        raise NotImplementedError

    def complete(self, request: ChatCompletionRequest) -> ChatCompletionResult:
        response = self.chat_completion(request)
        if response.message.tool_calls:
            raise LLMRequestError(
                "Model returned tool calls. Use the investigation agent for tool calling."
            )
        if not response.message.content or not response.message.content.strip():
            raise LLMRequestError("LLM returned empty content.")
        return ChatCompletionResult(
            content=response.message.content.strip(),
            model=response.model,
            provider=response.provider,
        )
