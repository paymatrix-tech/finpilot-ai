import re

from app.tools.exceptions import ToolError

PAYMENT_ID_PATTERN = re.compile(r"^PAY-[A-Z0-9]+(?:-[A-Z0-9]+)*$")
MAX_PAYMENT_ID_LENGTH = 64
MAX_INVESTIGATION_QUESTION_LENGTH = 2_000
MAX_LOG_SEARCH_QUERY_LENGTH = 500
MAX_DOC_SEARCH_QUERY_LENGTH = 2_000
MAX_DOC_SEARCH_LIMIT = 10
MIN_DOC_SEARCH_LIMIT = 1
MAX_PAYMENT_LIST_QUERY_LENGTH = 200


class InvalidPaymentIdError(ValueError):
    pass


def validate_payment_id(payment_id: str) -> str:
    normalized = payment_id.strip()
    if not normalized:
        raise InvalidPaymentIdError("payment_id is required.")
    if len(normalized) > MAX_PAYMENT_ID_LENGTH:
        raise InvalidPaymentIdError("payment_id is too long.")
    if not PAYMENT_ID_PATTERN.match(normalized):
        raise InvalidPaymentIdError(
            "payment_id must look like PAY-1001 or PAY-TEST-1001 (letters, numbers, hyphens)."
        )
    return normalized


def validate_payment_id_tool(payment_id: str) -> str:
    try:
        return validate_payment_id(payment_id)
    except InvalidPaymentIdError as exc:
        raise ToolError(str(exc)) from exc


def validate_investigation_question(question: str) -> str:
    normalized = question.strip()
    if not normalized:
        raise ValueError("question is required.")
    if len(normalized) > MAX_INVESTIGATION_QUESTION_LENGTH:
        raise ValueError(
            f"question must be at most {MAX_INVESTIGATION_QUESTION_LENGTH} characters."
        )
    return normalized


def clamp_doc_search_limit(limit: int) -> int:
    return max(MIN_DOC_SEARCH_LIMIT, min(limit, MAX_DOC_SEARCH_LIMIT))


def normalize_bounded_text(value: str, *, max_length: int, field_name: str) -> str:
    normalized = value.strip()
    if len(normalized) > max_length:
        raise ToolError(f"{field_name} must be at most {max_length} characters.")
    return normalized
