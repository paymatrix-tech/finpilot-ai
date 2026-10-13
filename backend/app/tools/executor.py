import json
from typing import Any

from app.security.tools import assert_read_only_tool
from app.security.validation import (
    clamp_doc_search_limit,
    normalize_bounded_text,
    validate_payment_id_tool,
    MAX_DOC_SEARCH_QUERY_LENGTH,
    MAX_LOG_SEARCH_QUERY_LENGTH,
)
from app.tools.documentation import DocumentationTools
from app.tools.exceptions import PaymentNotFoundError, ToolError
from app.tools.payment import PaymentTools


class PaymentToolExecutor:
    def __init__(
        self,
        tools: PaymentTools,
        documentation_tools: DocumentationTools | None = None,
    ) -> None:
        self._tools = tools
        self._documentation_tools = documentation_tools

    def execute(self, name: str, arguments: dict[str, Any]) -> Any:
        try:
            assert_read_only_tool(name)

            if name == "get_payment":
                payment_id = validate_payment_id_tool(_require_str(arguments, "payment_id"))
                return self._tools.get_payment(payment_id).model_dump(mode="json")

            if name == "get_payment_events":
                payment_id = validate_payment_id_tool(_require_str(arguments, "payment_id"))
                events = self._tools.get_payment_events(payment_id)
                return [event.model_dump(mode="json") for event in events]

            if name == "search_logs":
                payment_id = validate_payment_id_tool(_require_str(arguments, "payment_id"))
                query = arguments.get("query")
                if query is not None and not isinstance(query, str):
                    raise ToolError("search_logs query must be a string when provided.")
                if isinstance(query, str) and query.strip():
                    query = normalize_bounded_text(
                        query,
                        max_length=MAX_LOG_SEARCH_QUERY_LENGTH,
                        field_name="search_logs query",
                    )
                logs = self._tools.search_logs(payment_id, query=query)
                return [log.model_dump(mode="json") for log in logs]

            if name == "search_payment_docs":
                if self._documentation_tools is None:
                    raise ToolError("Documentation search is not configured.")
                query = normalize_bounded_text(
                    _require_str(arguments, "query"),
                    max_length=MAX_DOC_SEARCH_QUERY_LENGTH,
                    field_name="search_payment_docs query",
                )
                limit = arguments.get("limit", 5)
                if not isinstance(limit, int):
                    raise ToolError("search_payment_docs limit must be an integer when provided.")
                limit = clamp_doc_search_limit(limit)
                results = self._documentation_tools.search_payment_docs(query, limit=limit)
                return [result.model_dump(mode="json") for result in results]

            raise ToolError(f"Unknown tool '{name}'.")
        except PaymentNotFoundError as exc:
            return {"error": "payment_not_found", "payment_id": exc.payment_id, "message": str(exc)}
        except ToolError as exc:
            return {"error": "tool_error", "message": str(exc)}


def parse_tool_arguments(raw_arguments: str) -> dict[str, Any]:
    if not raw_arguments.strip():
        return {}
    try:
        parsed = json.loads(raw_arguments)
    except json.JSONDecodeError as exc:
        raise ToolError(f"Tool arguments must be valid JSON: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ToolError("Tool arguments must be a JSON object.")
    return parsed


def _require_str(arguments: dict[str, Any], key: str) -> str:
    value = arguments.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ToolError(f"{key} is required and must be a non-empty string.")
    return value.strip()
