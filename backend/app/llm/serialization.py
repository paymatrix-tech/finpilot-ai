from typing import Any

from app.llm.types import ChatMessage, ToolCall


def chat_message_to_payload(message: ChatMessage) -> dict[str, Any]:
    payload: dict[str, Any] = {"role": message.role}
    if message.content is not None:
        payload["content"] = message.content
    elif message.role == "assistant" and message.tool_calls:
        payload["content"] = None

    if message.tool_calls:
        payload["tool_calls"] = [_tool_call_to_payload(tool_call) for tool_call in message.tool_calls]

    if message.tool_call_id is not None:
        payload["tool_call_id"] = message.tool_call_id
    if message.name is not None:
        payload["name"] = message.name

    return payload


def _tool_call_to_payload(tool_call: ToolCall) -> dict[str, Any]:
    item: dict[str, Any] = {
        "id": tool_call.id,
        "type": "function",
        "function": {
            "name": tool_call.name,
            "arguments": tool_call.arguments,
        },
    }
    if tool_call.extra_content is not None:
        item["extra_content"] = tool_call.extra_content
    return item
