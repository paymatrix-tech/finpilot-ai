import json

import httpx
import pytest

from app.config import settings
from app.embeddings.factory import create_embedding_client, reset_embedding_client_cache
from app.embeddings.openai_compat import OpenAICompatibleEmbeddingClient
from app.embeddings.stub import StubEmbeddingClient


def test_stub_embedding_is_deterministic_and_normalized() -> None:
    client = StubEmbeddingClient(dimensions=1536)
    first = client.embed_documents(["ACH return code R01"])[0]
    second = client.embed_documents(["ACH return code R01"])[0]
    assert first == second
    assert len(first) == 1536
    norm = sum(value * value for value in first)
    assert abs(norm - 1.0) < 1e-6


def test_openai_compatible_embedding_client_parses_response() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/embeddings")
        body = json.loads(request.content)
        assert body["model"] == "text-embedding-3-small"
        assert body["input"] == ["hello", "world"]
        return httpx.Response(
            200,
            json={
                "data": [
                    {"index": 0, "embedding": [0.1, 0.2, 0.3]},
                    {"index": 1, "embedding": [0.4, 0.5, 0.6]},
                ]
            },
        )

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    client = OpenAICompatibleEmbeddingClient(
        provider="openai_compat",
        api_key="secret",
        model="text-embedding-3-small",
        base_url="https://example.test/v1",
        dimensions=3,
        http_client=http_client,
    )
    vectors = client.embed_documents(["hello", "world"])
    assert vectors == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]


def test_embedding_factory_defaults_to_stub(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "embedding_provider", "stub")
    reset_embedding_client_cache()
    client = create_embedding_client()
    assert client.provider == "stub"
    assert len(client.embed_documents(["ping"])[0]) == settings.embedding_dimensions
