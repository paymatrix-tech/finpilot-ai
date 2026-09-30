from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_REPO_ROOT = Path(__file__).resolve().parents[2]
_ENV_CANDIDATES = (_REPO_ROOT / ".env", _REPO_ROOT / "backend" / ".env")


def _existing_env_files() -> tuple[str, ...]:
    return tuple(str(path) for path in _ENV_CANDIDATES if path.is_file())


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://finpilot:finpilot@localhost:5432/finpilot"

    # LLM (Day 8+). Default stub works without an API key; set LLM_PROVIDER=openai for real calls.
    llm_provider: str = "stub"
    llm_api_key: str | None = None
    llm_model: str | None = None
    llm_base_url: str | None = None
    llm_timeout_seconds: float = 60.0
    # auto/smart: try providers in order (e.g. groq,gemini,stub)
    llm_route_order: str = "groq,gemini,openai,stub"
    groq_api_key: str | None = None
    gemini_api_key: str | None = None
    openai_api_key: str | None = None
    groq_model: str | None = None
    gemini_model: str | None = None
    openai_model: str | None = None

    # Embeddings (Day 12+). Default stub works without an API key.
    embedding_provider: str = "stub"
    embedding_model: str | None = None
    embedding_dimensions: int = 1536

    model_config = SettingsConfigDict(
        env_file=_existing_env_files() or (str(_REPO_ROOT / ".env"),),
        extra="ignore",
    )


settings = Settings()
