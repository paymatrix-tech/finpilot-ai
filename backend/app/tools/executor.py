import json
from typing import Any

from app.tools.exceptions import PaymentNotFoundError, ToolError
from app.tools.payment import PaymentTools


class PaymentToolExecutor:
    def __init__(self, tools: PaymentTools) -> None:
        self._tools = tools

    def execute(self, name: str, arguments: dict[str, Any]) -> Any:
        try:
            if name == "get_payment":
                payment_id = _require_str(arguments, "payment_id")
                return self._tools.get_payment(payment_id).model_dump(mode="json")

            if name == "get_payment_events":
                payment_id = _require_str(arguments, "payment_id")
                events = self._tools.get_payment_events(payment_id)
                return [event.model_dump(mode="json") for event in events]

            if name == "search_logs":
                payment_id = _require_str(arguments, "payment_id")
                query = arguments.get("query")
                if query is not None and not isinstance(query, str):
                    raise ToolError("search_logs query must be a string when provided.")
                logs = self._tools.search_logs(payment_id, query=query)
                return [log.model_dump(mode="json") for log in logs]

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
