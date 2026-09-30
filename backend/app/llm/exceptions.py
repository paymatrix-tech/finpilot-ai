class LLMError(Exception):
    """Base error for LLM integration."""


class LLMConfigurationError(LLMError):
    """LLM is not configured (missing key, model, etc.)."""


class LLMRequestError(LLMError):
    """The upstream model provider returned an error or invalid response."""


class LLMRateLimitError(LLMRequestError):
    """The upstream model provider rejected the request due to rate limits or quota."""

    def __init__(
        self,
        message: str,
        *,
        retry_after_seconds: float | None = None,
    ) -> None:
        super().__init__(message)
        self.retry_after_seconds = retry_after_seconds

    def user_message(self) -> str:
        if self.retry_after_seconds is not None:
            seconds = max(1, int(round(self.retry_after_seconds)))
            return (
                "The AI provider rate limit was reached. "
                f"Try again in about {seconds} seconds."
            )
        return (
            "The AI provider rate limit was reached. "
            "Wait a minute and try again."
        )
