from app.tools.exceptions import ToolError

# Import submodule directly so `app.tools` package __init__ is not loaded.
from app.tools.definitions import PAYMENT_INVESTIGATION_TOOLS

READ_ONLY_INVESTIGATION_TOOL_NAMES: frozenset[str] = frozenset(
    item["function"]["name"] for item in PAYMENT_INVESTIGATION_TOOLS
)

_WRITE_TOOL_MARKERS = (
    "delete",
    "update",
    "insert",
    "create",
    "drop",
    "execute",
    "run_sql",
    "write",
)


def assert_read_only_tool(name: str) -> None:
    lowered = name.strip().lower()
    if not lowered:
        raise ToolError("Tool name is required.")
    if lowered not in READ_ONLY_INVESTIGATION_TOOL_NAMES:
        raise ToolError(f"Unknown tool '{name}'.")
    if any(marker in lowered for marker in _WRITE_TOOL_MARKERS):
        raise ToolError(f"Tool '{name}' is not allowed (read-only investigation tools only).")
