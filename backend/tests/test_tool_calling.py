import json

import httpx
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.llm.base import LLMClient
from app.llm.types import (
    AssistantMessage,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ToolCall,
)
from app.models import Payment
from app.repositories.payment import PaymentRepository
from app.services.investigation_agent import InvestigationAgent
from app.tools.executor import PaymentToolExecutor, parse_tool_arguments
from app.tools.payment import PaymentTools


class SequenceLLM(LLMClient):
    def __init__(self, responses: list[ChatCompletionResponse]) -> None:
        self._responses = responses
        self.calls = 0

    @property
    def provider(self) -> str:
        return "sequence-test"

    def chat_completion(self, request: ChatCompletionRequest) -> ChatCompletionResponse:
        response = self._responses[self.calls]
        self.calls += 1
        if request.tools:
            assert len(request.tools) == 3
        return response


def test_parse_tool_arguments_requires_object() -> None:
    with pytest.raises(Exception):
        parse_tool_arguments("[]")


def test_investigation_agent_runs_tools_then_answers(
    db: Session, sample_payments: list[Payment]
) -> None:
    payment_id = sample_payments[0].id
    llm = SequenceLLM(
        [
            ChatCompletionResponse(
                message=AssistantMessage(
                    content=None,
                    tool_calls=[
                        ToolCall(
                            id="call-1",
                            name="get_payment",
                            arguments=json.dumps({"payment_id": payment_id}),
                        ),
                        ToolCall(
                            id="call-2",
                            name="search_logs",
                            arguments=json.dumps({"payment_id": payment_id, "query": "R01"}),
                        ),
                    ],
                ),
                model="test-model",
                provider="sequence-test",
            ),
            ChatCompletionResponse(
                message=AssistantMessage(
                    content="The payment failed because the gateway returned error code R01."
                ),
                model="test-model",
                provider="sequence-test",
            ),
        ]
    )
    tools = PaymentTools(PaymentRepository(db))
    agent = InvestigationAgent(llm, PaymentToolExecutor(tools))

    result = agent.investigate(payment_id, "Why did this payment fail?")

    assert llm.calls == 2
    assert len(result.steps) == 2
    assert result.steps[0].tool == "get_payment"
    assert result.steps[0].result["error_code"] == "R01"
    assert result.steps[1].tool == "search_logs"
    assert "R01" in result.steps[1].result[0]["message"]
    assert "R01" in result.answer


def test_openai_compatible_client_parses_tool_calls() -> None:
    from app.llm.openai_compat import OpenAICompatibleClient
    from app.llm.types import ChatMessage

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        assert body.get("tools")
        return httpx.Response(
            200,
            json={
                "model": "test-model",
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": None,
                            "tool_calls": [
                                {
                                    "id": "call_abc",
                                    "type": "function",
                                    "function": {
                                        "name": "get_payment",
                                        "arguments": '{"payment_id":"PAY-1"}',
                                    },
                                }
                            ],
                        }
                    }
                ],
            },
        )

    http_client = httpx.Client(transport=httpx.MockTransport(handler))
    client = OpenAICompatibleClient(
        provider="openai_compat",
        api_key="secret",
        model="test-model",
        base_url="https://example.test/v1",
        http_client=http_client,
    )
    response = client.chat_completion(
        ChatCompletionRequest(
            messages=[ChatMessage(role="user", content="investigate")],
            tools=[{"type": "function", "function": {"name": "get_payment"}}],
        )
    )
    assert len(response.message.tool_calls) == 1
    assert response.message.tool_calls[0].name == "get_payment"


def test_investigation_query_endpoint(
    client: TestClient, sample_payments: list[Payment], monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.routers.investigation import get_investigation_agent

    payment_id = sample_payments[0].id

    class FakeAgent:
        def investigate(self, pid: str, question: str):
            from app.schemas import InvestigationQueryResponse, ToolExecutionStep

            assert pid == payment_id
            assert question
            return InvestigationQueryResponse(
                answer="Failed with R01.",
                steps=[
                    ToolExecutionStep(
                        tool="get_payment",
                        arguments={"payment_id": pid},
                        result={"error_code": "R01"},
                    )
                ],
                model="fake",
                provider="fake",
            )

    client.app.dependency_overrides[get_investigation_agent] = lambda: FakeAgent()
    response = client.post(
        "/api/investigations/query",
        json={"payment_id": payment_id, "question": "Why failed?"},
    )
    client.app.dependency_overrides.clear()

    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "Failed with R01."
    assert body["steps"][0]["tool"] == "get_payment"
