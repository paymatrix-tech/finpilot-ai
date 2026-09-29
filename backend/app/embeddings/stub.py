import hashlib
import math

from app.embeddings.base import EmbeddingClient
from app.embeddings.exceptions import EmbeddingRequestError


class StubEmbeddingClient(EmbeddingClient):
    """Deterministic embeddings for local development and tests without an API key."""

    def __init__(self, *, dimensions: int = 1536, model: str = "stub-embedding") -> None:
        if dimensions < 1:
            raise EmbeddingRequestError("dimensions must be positive.")
        self._dimensions = dimensions
        self._model = model

    @property
    def provider(self) -> str:
        return "stub"

    @property
    def model(self) -> str:
        return self._model

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [_stub_vector(text, self._dimensions) for text in texts]


def _stub_vector(text: str, dimensions: int) -> list[float]:
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    values = [(digest[index % len(digest)] / 255.0) * 2 - 1 for index in range(dimensions)]
    norm = math.sqrt(sum(value * value for value in values))
    if norm == 0:
        return values
    return [value / norm for value in values]
