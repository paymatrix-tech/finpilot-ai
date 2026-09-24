from abc import ABC, abstractmethod

from app.llm.types import ChatCompletionRequest, ChatCompletionResult


class LLMClient(ABC):
    @property
    @abstractmethod
    def provider(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def complete(self, request: ChatCompletionRequest) -> ChatCompletionResult:
        raise NotImplementedError
