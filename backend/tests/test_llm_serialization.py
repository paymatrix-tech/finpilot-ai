from app.llm.serialization import chat_message_to_payload
from app.llm.types import ChatMessage, ToolCall


def test_chat_message_to_payload_preserves_gemini_thought_signature() -> None:
    signature = {
        "google": {
            "thought_signature": "encrypted-signature-value",
        }
    }
    message = ChatMessage(
        role="assistant",
        content=None,
        tool_calls=[
            ToolCall(
                id="call_1",
                name="get_payment",
                arguments='{"payment_id":"PAY-1001"}',
                extra_content=signature,
            )
        ],
    )

    payload = chat_message_to_payload(message)
    assert payload["tool_calls"][0]["extra_content"] == signature


def test_chat_message_to_payload_omits_extra_content_when_absent() -> None:
    message = ChatMessage(
        role="assistant",
        content=None,
        tool_calls=[
            ToolCall(
                id="call_1",
                name="get_payment",
                arguments="{}",
            )
        ],
    )

    payload = chat_message_to_payload(message)
    assert "extra_content" not in payload["tool_calls"][0]
