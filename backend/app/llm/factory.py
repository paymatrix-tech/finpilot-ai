from functools import lru_cache

from app.config import settings
from app.llm.base import LLMClient
from app.llm.exceptions import LLMConfigurationError
from app.llm.groq_models import resolve_groq_model
from app.llm.openai_compat import OpenAICompatibleClient
from app.llm.routing import RoutingLLMClient
from app.llm.stub import StubLLMClient

OPENAI_DEFAULT_BASE_URL = "https://api.openai.com/v1"
GEMINI_DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai"
GROQ_DEFAULT_BASE_URL = "https://api.groq.com/openai/v1"
MLX_DEFAULT_BASE_URL = "http://127.0.0.1:8080/v1"

DEFAULT_ROUTE_ORDER = ("groq", "gemini", "openai", "stub")
PROVIDER_ALIASES = {"smart": "auto", "router": "auto"}


def create_llm_client() -> LLMClient:
    provider = settings.llm_provider.lower().strip()
    provider = PROVIDER_ALIASES.get(provider, provider)

    if provider in {"auto", "router"}:
        return _create_routing_client()

    client = _try_create_provider_client(provider)
    if client is None:
        raise LLMConfigurationError(_provider_config_error(provider))
    return client


def _create_routing_client() -> LLMClient:
    order = _parse_route_order(settings.llm_route_order)
    clients: list[tuple[str, LLMClient]] = []

    for name in order:
        client = _try_create_provider_client(name)
        if client is not None:
            clients.append((name, client))

    if not clients:
        raise LLMConfigurationError(
            "Smart routing (LLM_PROVIDER=auto) found no configured providers. "
            "Set GROQ_API_KEY, GEMINI_API_KEY, OPENAI_API_KEY, or include stub in LLM_ROUTE_ORDER."
        )
    if len(clients) == 1:
        return clients[0][1]
    return RoutingLLMClient(clients)


def _parse_route_order(raw: str) -> tuple[str, ...]:
    names = [part.strip().lower() for part in raw.split(",") if part.strip()]
    if not names:
        return DEFAULT_ROUTE_ORDER
    return tuple(names)


def _try_create_provider_client(provider: str) -> LLMClient | None:
    if provider == "stub":
        return StubLLMClient(model=settings.llm_model or "stub")

    if provider == "mlx":
        mode = settings.llm_provider.lower().strip()
        if mode not in {"mlx", "auto", "smart", "router"} and not settings.llm_base_url:
            return None
        base_url = settings.llm_base_url or MLX_DEFAULT_BASE_URL
        model = settings.llm_model or "local"
        return OpenAICompatibleClient(
            provider="mlx",
            api_key=settings.llm_api_key,
            model=model,
            base_url=base_url,
            timeout_seconds=settings.llm_timeout_seconds,
        )

    api_key = _api_key_for(provider)
    if not api_key:
        return None

    if provider == "gemini":
        model = settings.gemini_model or settings.llm_model or "gemini-2.0-flash"
        base_url = GEMINI_DEFAULT_BASE_URL
        if settings.llm_provider.lower() == "gemini" and settings.llm_base_url:
            base_url = settings.llm_base_url
        return OpenAICompatibleClient(
            provider="gemini",
            api_key=api_key,
            model=model,
            base_url=base_url,
            timeout_seconds=settings.llm_timeout_seconds,
        )

    if provider == "groq":
        model = resolve_groq_model(settings.groq_model or settings.llm_model)
        return OpenAICompatibleClient(
            provider="groq",
            api_key=api_key,
            model=model,
            base_url=GROQ_DEFAULT_BASE_URL,
            timeout_seconds=settings.llm_timeout_seconds,
        )

    if provider in {"openai", "openai_compat"}:
        model = settings.openai_model or settings.llm_model or "gpt-4o-mini"
        return OpenAICompatibleClient(
            provider=provider,
            api_key=api_key,
            model=model,
            base_url=OPENAI_DEFAULT_BASE_URL,
            timeout_seconds=settings.llm_timeout_seconds,
        )

    return None


def _api_key_for(provider: str) -> str | None:
    mode = settings.llm_provider.lower().strip()

    if provider == "groq":
        if settings.groq_api_key:
            return settings.groq_api_key
        if mode in {"groq", "auto", "smart", "router"}:
            return settings.llm_api_key
        return None

    if provider == "gemini":
        if settings.gemini_api_key:
            return settings.gemini_api_key
        if mode == "gemini":
            return settings.llm_api_key
        return None

    if provider in {"openai", "openai_compat"}:
        if settings.openai_api_key:
            return settings.openai_api_key
        if mode in {"openai", "openai_compat"}:
            return settings.llm_api_key
        return None

    return None


def _provider_config_error(provider: str) -> str:
    if provider == "groq":
        return "GROQ_API_KEY or LLM_API_KEY is required when LLM_PROVIDER is groq."
    if provider == "gemini":
        return "GEMINI_API_KEY or LLM_API_KEY is required when LLM_PROVIDER is gemini."
    if provider in {"openai", "openai_compat"}:
        return "OPENAI_API_KEY or LLM_API_KEY is required when LLM_PROVIDER is openai."
    return (
        f"Unsupported LLM_PROVIDER '{settings.llm_provider}'. "
        "Use auto, groq, gemini, openai, openai_compat, mlx, or stub."
    )


@lru_cache
def get_llm_client() -> LLMClient:
    return create_llm_client()


def reset_llm_client_cache() -> None:
    get_llm_client.cache_clear()
