from app.api_errors import error_detail
from app.llm.exceptions import (
    LLMConfigurationError,
    LLMRateLimitError,
    LLMRequestError,
)


def llm_error_sse_payload(exc: Exception) -> dict[str, object]:
    if isinstance(exc, LLMConfigurationError):
        return error_detail("llm_unavailable", str(exc))
    if isinstance(exc, LLMRateLimitError):
        fields: dict[str, object] = {}
        if exc.retry_after_seconds is not None:
            fields["retry_after_seconds"] = max(1, int(round(exc.retry_after_seconds)))
        return error_detail("llm_rate_limited", exc.user_message(), **fields)
    if isinstance(exc, LLMRequestError):
        return error_detail("llm_request_failed", str(exc))
    return error_detail("llm_request_failed", "Investigation failed.")