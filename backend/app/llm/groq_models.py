import logging

logger = logging.getLogger(__name__)

# Groq shutdown list: https://console.groq.com/docs/deprecations
GROQ_DEPRECATED_MODELS: dict[str, str] = {
    "llama-3.3-70b-versatile": "openai/gpt-oss-120b",
    "llama-3.1-8b-instant": "openai/gpt-oss-20b",
}

GROQ_DEFAULT_MODEL = "openai/gpt-oss-120b"


def resolve_groq_model(model: str | None) -> str:
    raw = (model or "").strip()
    if not raw:
        return GROQ_DEFAULT_MODEL
    replacement = GROQ_DEPRECATED_MODELS.get(raw)
    if replacement:
        logger.warning(
            "Groq model %s is retired; using %s instead. Update GROQ_MODEL in .env.",
            raw,
            replacement,
        )
        return replacement
    return raw
