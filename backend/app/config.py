from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "postgresql+psycopg://finpilot:finpilot@localhost:5432/finpilot"

    # LLM (Day 8+). Default stub works without an API key; set LLM_PROVIDER=openai for real calls.
    llm_provider: str = "stub"
    llm_api_key: str | None = None
    llm_model: str | None = None
    llm_base_url: str | None = None
    llm_timeout_seconds: float = 60.0

    # Embeddings (Day 12+). Default stub works without an API key.
    embedding_provider: str = "stub"
    embedding_model: str | None = None
    embedding_dimensions: int = 1536

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        extra="ignore",
    )


settings = Settings()
