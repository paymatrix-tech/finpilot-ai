class LLMError(Exception):
    """Base error for LLM integration."""


class LLMConfigurationError(LLMError):
    """LLM is not configured (missing key, model, etc.)."""


class LLMRequestError(LLMError):
    """The upstream model provider returned an error or invalid response."""
