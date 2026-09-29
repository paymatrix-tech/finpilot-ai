import json

import pytest

from app.llm.exceptions import LLMRequestError
from app.services.rca import InvestigationRCA, parse_rca_response


def test_parse_rca_response_accepts_fenced_json() -> None:
    payload = {
        "root_cause": "Insufficient funds",
        "confidence": "high",
        "evidence": ["Gateway returned R01"],
        "recommendation": "Do not retry immediately",
        "sources": ["ach-error-codes.md"],
    }
    raw = f"```json\n{json.dumps(payload)}\n```"
    rca = parse_rca_response(raw)
    assert rca.root_cause == "Insufficient funds"
    assert rca.normalized_confidence() == "high"
    assert rca.sources == ["ach-error-codes.md"]


def test_parse_rca_response_rejects_invalid_payload() -> None:
    with pytest.raises(LLMRequestError):
        parse_rca_response("not json")


def test_investigation_rca_to_answer() -> None:
    rca = InvestigationRCA(
        root_cause="Gateway timeout",
        confidence="medium",
        evidence=["No gateway response within SLA"],
        recommendation="Retry with backoff",
        sources=["timeout-handling.md"],
    )
    assert "Gateway timeout" in rca.to_answer()
    assert "Retry with backoff" in rca.to_answer()
