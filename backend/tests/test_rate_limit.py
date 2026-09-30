import json

from app.llm.exceptions import LLMRateLimitError
from app.llm.openai_compat import OpenAICompatibleClient
from app.llm.rate_limit import parse_retry_after_seconds
from app.llm.types import ChatCompletionRequest, ChatMessage
import httpx
import pytest

def test_parse_retry_after_seconds_from_gemini_payload() -> None:
    payload = [
        {
            "error": {
                "code": 429,
                "message": "Please retry in 45.391664692s.",
                "details": [
                    {
                        "@type": "type.googleapis.com/google.rpc.RetryInfo",
                        "retryDelay": "45s",
                    }
                ],
            }
        }
    ]
    assert parse_retry_after_seconds(json.dumps(payload)) == 45.0


def test_openai_compatible_client_maps_429_to_rate_limit_error() -> None:
    body = json.dumps(
        [
            {
                "error": {
                    "message": "Quota exceeded. Please retry in 12.5s.",
                    "details": [{"retryDelay": "12s"}],
                }
            }
        ]
    )

    def handler(_request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, text=body)

    client = OpenAICompatibleClient(
        provider="gemini",
        api_key="secret",
        model="gemini-test",
        base_url="https://example.test/v1",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )

    with pytest.raises(LLMRateLimitError) as exc_info:
        client.chat_completion(ChatCompletionRequest(messages=[ChatMessage(role="user", content="hi")]))

    assert exc_info.value.retry_after_seconds == 12.0
    assert "12 seconds" in exc_info.value.user_message()
