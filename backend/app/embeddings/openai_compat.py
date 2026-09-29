from typing import Any

import httpx

from app.embeddings.base import EmbeddingClient
from app.embeddings.exceptions import EmbeddingConfigurationError, EmbeddingRequestError


class OpenAICompatibleEmbeddingClient(EmbeddingClient):
    """Embeddings against an OpenAI-compatible HTTP API."""

    def __init__(
        self,
        *,
        provider: str,
        api_key: str | None,
        model: str,
        base_url: str,
        dimensions: int,
        timeout_seconds: float = 60.0,
        http_client: httpx.Client | None = None,
    ) -> None:
        if not model.strip():
            raise EmbeddingConfigurationError("EMBEDDING_MODEL or LLM_MODEL is required.")
        self._provider = provider
        self._api_key = api_key
        self._model = model.strip()
        self._base_url = base_url.rstrip("/")
        self._dimensions = dimensions
        self._timeout = timeout_seconds
        self._http = http_client or httpx.Client(timeout=timeout_seconds)

    @property
    def provider(self) -> str:
        return self._provider

    @property
    def model(self) -> str:
        return self._model

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"

        payload: dict[str, Any] = {"model": self._model, "input": texts}
        if self._dimensions:
            payload["dimensions"] = self._dimensions

        url = f"{self._base_url}/embeddings"
        try:
            response = self._http.post(url, headers=headers, json=payload)
        except httpx.HTTPError as exc:
            raise EmbeddingRequestError(f"Embedding request failed: {exc}") from exc

        if response.status_code >= 400:
            detail = response.text.strip() or response.reason_phrase
            raise EmbeddingRequestError(f"Embedding API returned {response.status_code}: {detail}")

        try:
            data = response.json()["data"]
            ordered = sorted(data, key=lambda item: item["index"])
            vectors = [item["embedding"] for item in ordered]
        except (KeyError, TypeError, ValueError) as exc:
            raise EmbeddingRequestError("Embedding response was missing vectors.") from exc

        for vector in vectors:
            if len(vector) != self._dimensions:
                raise EmbeddingRequestError(
                    f"Expected embedding dimension {self._dimensions}, got {len(vector)}."
                )
        return vectors
