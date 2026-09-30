from typing import Any

from fastapi import HTTPException, status
from sqlalchemy.exc import SQLAlchemyError


class ErrorDetail:
    PAYMENT_NOT_FOUND = "payment_not_found"
    DATABASE_ERROR = "database_error"
    LLM_UNAVAILABLE = "llm_unavailable"
    LLM_REQUEST_FAILED = "llm_request_failed"
    LLM_RATE_LIMITED = "llm_rate_limited"
    INVESTIGATION_NOT_FOUND = "investigation_not_found"


def error_detail(code: str, message: str, **fields: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {"code": code, "message": message}
    payload.update(fields)
    return payload


def http_error(
    status_code: int,
    *,
    code: str,
    message: str,
) -> HTTPException:
    return HTTPException(status_code=status_code, detail=error_detail(code, message))


def payment_not_found(payment_id: str) -> HTTPException:
    return http_error(
        status.HTTP_404_NOT_FOUND,
        code=ErrorDetail.PAYMENT_NOT_FOUND,
        message=f"Payment {payment_id} was not found.",
    )


def investigation_not_found(investigation_id: int) -> HTTPException:
    return http_error(
        status.HTTP_404_NOT_FOUND,
        code=ErrorDetail.INVESTIGATION_NOT_FOUND,
        message=f"Investigation {investigation_id} was not found.",
    )


def database_error(message: str = "The database is temporarily unavailable.") -> HTTPException:
    return http_error(
        status.HTTP_503_SERVICE_UNAVAILABLE,
        code=ErrorDetail.DATABASE_ERROR,
        message=message,
    )


def llm_unavailable(message: str) -> HTTPException:
    return http_error(
        status.HTTP_503_SERVICE_UNAVAILABLE,
        code=ErrorDetail.LLM_UNAVAILABLE,
        message=message,
    )


def llm_request_failed(message: str) -> HTTPException:
    return http_error(
        status.HTTP_502_BAD_GATEWAY,
        code=ErrorDetail.LLM_REQUEST_FAILED,
        message=message,
    )


def llm_rate_limited(
    message: str,
    *,
    retry_after_seconds: float | None = None,
) -> HTTPException:
    fields: dict[str, Any] = {}
    if retry_after_seconds is not None:
        fields["retry_after_seconds"] = max(1, int(round(retry_after_seconds)))
    return HTTPException(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        detail=error_detail(ErrorDetail.LLM_RATE_LIMITED, message, **fields),
    )


def raise_for_llm_error(exc: Exception) -> None:
    from app.llm.exceptions import (
        LLMConfigurationError,
        LLMRateLimitError,
        LLMRequestError,
    )

    if isinstance(exc, LLMConfigurationError):
        raise llm_unavailable(str(exc)) from exc
    if isinstance(exc, LLMRateLimitError):
        raise llm_rate_limited(
            exc.user_message(),
            retry_after_seconds=exc.retry_after_seconds,
        ) from exc
    if isinstance(exc, LLMRequestError):
        raise llm_request_failed(str(exc)) from exc


def database_unavailable_exception(exc: SQLAlchemyError) -> HTTPException:
    return database_error(
        "Could not reach the database. Try again in a moment.",
    )


def parse_error_payload(detail: Any) -> tuple[str | None, str]:
    if isinstance(detail, dict):
        code = detail.get("code")
        message = detail.get("message")
        if isinstance(code, str) and isinstance(message, str):
            return code, message
    if isinstance(detail, str):
        return None, detail
    return None, "Request failed."
