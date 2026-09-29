from app.prompts.investigation import INSUFFICIENT_EVIDENCE_ROOT_CAUSE
from app.schemas import ToolExecutionStep
from app.services.rca import InvestigationRCA


def apply_evidence_requirements(
    rca: InvestigationRCA,
    *,
    steps: list[ToolExecutionStep],
) -> InvestigationRCA:
    evidence = [item.strip() for item in rca.evidence if item and item.strip()]
    sources = [item.strip() for item in rca.sources if item and item.strip()]
    root_cause = rca.root_cause.strip()
    recommendation = rca.recommendation.strip()
    confidence = rca.normalized_confidence()

    claims_conclusion = INSUFFICIENT_EVIDENCE_ROOT_CAUSE.lower() not in root_cause.lower()
    tools_used = {step.tool for step in steps}
    docs_tool_used = "search_payment_docs" in tools_used

    if claims_conclusion and not evidence:
        return _insufficient_rca(recommendation)

    if confidence == "high" and len(evidence) < 2:
        confidence = "medium" if evidence else "low"

    if confidence == "medium" and not evidence and claims_conclusion:
        confidence = "low"

    if docs_tool_used and claims_conclusion and confidence in {"high", "medium"} and not sources:
        confidence = "medium" if confidence == "high" else "low"

    if confidence == "low" and claims_conclusion and len(evidence) < 1:
        return _insufficient_rca(recommendation)

    if confidence == "low" and claims_conclusion and len(evidence) == 1:
        # Single weak fact — keep conclusion but align with low confidence.
        pass

    return InvestigationRCA(
        root_cause=root_cause,
        confidence=confidence,
        evidence=evidence[:8],
        recommendation=recommendation,
        sources=sources,
    )


def _insufficient_rca(recommendation: str) -> InvestigationRCA:
    fallback = "Gather payment events, logs, and documentation, then rerun the investigation."
    return InvestigationRCA(
        root_cause=INSUFFICIENT_EVIDENCE_ROOT_CAUSE,
        confidence="low",
        evidence=[],
        recommendation=recommendation or fallback,
        sources=[],
    )
