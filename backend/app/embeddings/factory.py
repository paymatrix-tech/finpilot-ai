from functools import lru_cache

from app.config import settings
from app.embeddings.base import EmbeddingClient
from app.embeddings.exceptions import EmbeddingConfigurationError
from app.embeddings.openai_compat import OpenAICompatibleEmbeddingClient
from app.embeddings.stub import StubEmbeddingClient
from app.llm.factory import GEMINI_DEFAULT_BASE_URL, MLX_DEFAULT_BASE_URL, OPENAI_DEFAULT_BASE_URL

OPENAI_DEFAULT_EMBEDDING_MODEL = "text-embedding-3-small"


def create_embedding_client() -> EmbeddingClient:
    provider = settings.embedding_provider.lower().strip()
    dimensions = settings.embedding_dimensions

    if provider == "stub":
        model = settings.embedding_model or "stub-embedding"
        return StubEmbeddingClient(dimensions=dimensions, model=model)

    if provider == "mlx":
        base_url = settings.llm_base_url or MLX_DEFAULT_BASE_URL
        model = settings.embedding_model or settings.llm_model or "local"
        return OpenAICompatibleEmbeddingClient(
            provider="mlx",
            api_key=settings.llm_api_key,
            model=model,
            base_url=base_url,
            dimensions=dimensions,
            timeout_seconds=settings.llm_timeout_seconds,
        )

    if provider == "gemini":
        if not settings.llm_api_key:
            raise EmbeddingConfigurationError(
                "LLM_API_KEY is required when EMBEDDING_PROVIDER is gemini."
            )
        base_url = settings.llm_base_url or GEMINI_DEFAULT_BASE_URL
        model = settings.embedding_model or "text-embedding-004"
        return OpenAICompatibleEmbeddingClient(
            provider="gemini",
            api_key=settings.llm_api_key,
            model=model,
            base_url=base_url,
            dimensions=dimensions,
            timeout_seconds=settings.llm_timeout_seconds,
        )

    if provider in {"openai", "openai_compat"}:
        if not settings.llm_api_key:
            raise EmbeddingConfigurationError(
                "LLM_API_KEY is required when EMBEDDING_PROVIDER is openai."
            )
        base_url = settings.llm_base_url or OPENAI_DEFAULT_BASE_URL
        model = settings.embedding_model or OPENAI_DEFAULT_EMBEDDING_MODEL
        return OpenAICompatibleEmbeddingClient(
            provider=provider,
            api_key=settings.llm_api_key,
            model=model,
            base_url=base_url,
            dimensions=dimensions,
            timeout_seconds=settings.llm_timeout_seconds,
        )

    raise EmbeddingConfigurationError(
        f"Unsupported EMBEDDING_PROVIDER '{settings.embedding_provider}'. "
        "Use stub, gemini, openai, openai_compat, or mlx."
    )


@lru_cache
def get_embedding_client() -> EmbeddingClient:
    return create_embedding_client()


def reset_embedding_client_cache() -> None:
    get_embedding_client.cache_clear()
