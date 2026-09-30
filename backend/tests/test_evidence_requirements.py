from app.schemas import ToolExecutionStep
from app.services.evidence_requirements import apply_evidence_requirements
from app.services.rca import InvestigationRCA


def test_high_confidence_downgraded_without_two_evidence_items() -> None:
    rca = InvestigationRCA(
        root_cause="Gateway timeout",
        confidence="high",
        evidence=["Single log line only"],
        recommendation="Retry with backoff",
        sources=["timeout-handling.md"],
    )
    adjusted = apply_evidence_requirements(
        rca,
        steps=[
            ToolExecutionStep(tool="get_payment", arguments={}, result={}),
            ToolExecutionStep(tool="search_logs", arguments={}, result=[]),
        ],
    )
    assert adjusted.normalized_confidence() == "medium"
    assert adjusted.root_cause == "Gateway timeout"


def test_missing_evidence_forces_insufficient_root_cause() -> None:
    rca = InvestigationRCA(
        root_cause="Insufficient funds",
        confidence="high",
        evidence=[],
        recommendation="Notify customer",
        sources=[],
    )
    adjusted = apply_evidence_requirements(rca, steps=[])
    assert "Insufficient evidence" in adjusted.root_cause
    assert adjusted.evidence == []
    assert adjusted.normalized_confidence() == "low"


def test_docs_tool_without_sources_downgrades_confidence() -> None:
    rca = InvestigationRCA(
        root_cause="Card declined",
        confidence="high",
        evidence=["Gateway returned 05", "Payment status FAILED"],
        recommendation="Do not retry",
        sources=[],
    )
    adjusted = apply_evidence_requirements(
        rca,
        steps=[ToolExecutionStep(tool="search_payment_docs", arguments={"query": "05"}, result=[])],
    )
    assert adjusted.normalized_confidence() == "medium"
