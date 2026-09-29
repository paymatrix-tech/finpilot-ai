from functools import lru_cache

from app.config import settings
from app.llm.base import LLMClient
from app.llm.exceptions import LLMConfigurationError
from app.llm.openai_compat import OpenAICompatibleClient
from app.llm.stub import StubLLMClient

OPENAI_DEFAULT_BASE_URL = "https://api.openai.com/v1"
GEMINI_DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai"
MLX_DEFAULT_BASE_URL = "http://127.0.0.1:8080/v1"


def create_llm_client() -> LLMClient:
    provider = settings.llm_provider.lower().strip()

    if provider == "stub":
        return StubLLMClient(model=settings.llm_model or "stub")

    if provider == "mlx":
        base_url = settings.llm_base_url or MLX_DEFAULT_BASE_URL
        model = settings.llm_model or "local"
        return OpenAICompatibleClient(
            provider="mlx",
            api_key=settings.llm_api_key,
            model=model,
            base_url=base_url,
            timeout_seconds=settings.llm_timeout_seconds,
        )

    if provider == "gemini":
        if not settings.llm_api_key:
            raise LLMConfigurationError("LLM_API_KEY is required when LLM_PROVIDER is gemini.")
        base_url = settings.llm_base_url or GEMINI_DEFAULT_BASE_URL
        model = settings.llm_model or "gemini-3.6-flash"
        return OpenAICompatibleClient(
            provider="gemini",
            api_key=settings.llm_api_key,
            model=model,
            base_url=base_url,
            timeout_seconds=settings.llm_timeout_seconds,
        )

    if provider in {"openai", "openai_compat"}:
        if not settings.llm_api_key:
            raise LLMConfigurationError("LLM_API_KEY is required when LLM_PROVIDER is openai.")
        base_url = settings.llm_base_url or OPENAI_DEFAULT_BASE_URL
        model = settings.llm_model or "gpt-4o-mini"
        return OpenAICompatibleClient(
            provider=provider,
            api_key=settings.llm_api_key,
            model=model,
            base_url=base_url,
            timeout_seconds=settings.llm_timeout_seconds,
        )

    raise LLMConfigurationError(
        f"Unsupported LLM_PROVIDER '{settings.llm_provider}'. "
        "Use stub, gemini, openai, openai_compat, or mlx."
    )


@lru_cache
def get_llm_client() -> LLMClient:
    return create_llm_client()


def reset_llm_client_cache() -> None:
    get_llm_client.cache_clear()
