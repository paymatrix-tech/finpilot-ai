import pytest

from app.llm.exceptions import LLMRateLimitError, LLMRequestError
from app.llm.routing import RoutingLLMClient
from app.llm.types import (
    AssistantMessage,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatMessage,
)
from app.llm.base import LLMClient


class StaticLLM(LLMClient):
    def __init__(self, provider_id: str, *, fail: bool = False, rate_limited: bool = False) -> None:
        self._provider_id = provider_id
        self._fail = fail
        self._rate_limited = rate_limited

    @property
    def provider(self) -> str:
        return self._provider_id

    def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        if self._rate_limited:
            raise LLMRateLimitError("rate limited", retry_after_seconds=30)
        if self._fail:
            raise LLMRequestError("LLM returned 503: unavailable")
        return ChatCompletionResponse(
            message=AssistantMessage(content=f"ok from {self._provider_id}"),
            model="test",
            provider=self._provider_id,
        )


def test_routing_falls_back_on_rate_limit() -> None:
    router = RoutingLLMClient(
        [
            ("groq", StaticLLM("groq", rate_limited=True)),
            ("stub", StaticLLM("stub")),
        ]
    )
    response = router.chat_completion(ChatCompletionRequest(messages=[ChatMessage(role="user", content="hi")]))
    assert response.provider == "stub"
    assert response.message.content == "ok from stub"


def test_routing_falls_back_on_transient_error() -> None:
    router = RoutingLLMClient(
        [
            ("groq", StaticLLM("groq", fail=True)),
            ("stub", StaticLLM("stub")),
        ]
    )
    response = router.chat_completion(ChatCompletionRequest(messages=[ChatMessage(role="user", content="hi")]))
    assert response.provider == "stub"


class ModelNotFoundLLM(LLMClient):
    @property
    def provider(self) -> str:
        return "groq"

    def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        raise LLMRequestError(
            'LLM returned 404: {"error":{"message":"The model `llama-3.3-70b-versatile` does not exist",'
            '"code":"model_not_found"}}'
        )


def test_routing_falls_back_on_unknown_model() -> None:
    router = RoutingLLMClient(
        [
            ("groq", ModelNotFoundLLM()),
            ("openai", StaticLLM("openai")),
        ]
    )
    response = router.chat_completion(ChatCompletionRequest(messages=[ChatMessage(role="user", content="hi")]))
    assert response.provider == "openai"


def test_routing_raises_when_all_providers_fail() -> None:
    router = RoutingLLMClient(
        [
            ("groq", StaticLLM("groq", rate_limited=True)),
            ("gemini", StaticLLM("gemini", rate_limited=True)),
        ]
    )
    with pytest.raises(LLMRateLimitError):
        router.chat_completion(ChatCompletionRequest(messages=[ChatMessage(role="user", content="hi")]))
