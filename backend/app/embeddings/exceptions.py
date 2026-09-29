class EmbeddingError(Exception):
    """Base error for embedding integration."""


class EmbeddingConfigurationError(EmbeddingError):
    """Embeddings are not configured (missing key, model, etc.)."""


class EmbeddingRequestError(EmbeddingError):
    """The upstream embedding provider returned an error or invalid response."""
