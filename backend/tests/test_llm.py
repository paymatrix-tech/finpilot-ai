import json

import httpx
import pytest
from fastapi.testclient import TestClient

from app.llm.exceptions import LLMConfigurationError
from app.llm.factory import create_llm_client, reset_llm_client_cache
from app.llm.openai_compat import OpenAICompatibleClient
from app.llm.types import ChatCompletionRequest, ChatMessage


def test_stub_client_echoes_last_user_message(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.config import settings

    monkeypatch.setattr(settings, "llm_provider", "stub")
    reset_llm_client_cache()
    client = create_llm_client()
    result = client.complete(
        ChatCompletionRequest(
            messages=[
                ChatMessage(role="system", content="You are helpful."),
                ChatMessage(role="user", content="Hello FinPilot"),
            ]
        )
    )
    assert result.provider == "stub"
    assert "Hello FinPilot" in result.content


def test_openai_compatible_client_parses_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/chat/completions")
        body = json.loads(request.content)
        assert body["model"] == "test-model"
        assert body["messages"][-1]["content"] == "ping"
        return httpx.Response(
            200,
            json={
                "model": "test-model",
                "choices": [{"message": {"role": "assistant", "content": "pong"}}],
            },
        )

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    client = OpenAICompatibleClient(
        provider="openai_compat",
        api_key="secret",
        model="test-model",
        base_url="https://example.test/v1",
        http_client=http_client,
    )
    result = client.complete(
        ChatCompletionRequest(messages=[ChatMessage(role="user", content="ping")])
    )
    assert result.content == "pong"
    assert result.model == "test-model"


def test_create_gemini_client_uses_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.config import settings

    monkeypatch.setattr(settings, "llm_provider", "gemini")
    monkeypatch.setattr(settings, "llm_api_key", "test-key")
    monkeypatch.setattr(settings, "llm_model", None)
    monkeypatch.setattr(settings, "llm_base_url", None)
    reset_llm_client_cache()
    client = create_llm_client()
    assert client.provider == "gemini"


def test_create_openai_client_requires_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.config import settings

    monkeypatch.setattr(settings, "llm_provider", "openai")
    monkeypatch.setattr(settings, "llm_api_key", None)
    reset_llm_client_cache()
    with pytest.raises(LLMConfigurationError):
        create_llm_client()


def test_llm_chat_endpoint_with_stub(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.config import settings
    from app.llm.factory import get_llm_client

    monkeypatch.setattr(settings, "llm_provider", "stub")
    reset_llm_client_cache()
    client.app.dependency_overrides[get_llm_client] = create_llm_client

    response = client.post(
        "/api/llm/chat",
        json={"messages": [{"role": "user", "content": "Say hi"}]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == "stub"
    assert "Say hi" in body["content"]

    client.app.dependency_overrides.clear()
    reset_llm_client_cache()
