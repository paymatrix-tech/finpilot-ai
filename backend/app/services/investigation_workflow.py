from app.schemas import InvestigationQueryResponse, ToolExecutionStep
from app.services.rca import InvestigationRCA


def build_investigation_response(
    *,
    payment_id: str,
    question: str,
    steps: list[ToolExecutionStep],
    rca: InvestigationRCA,
    model: str,
    provider: str,
) -> InvestigationQueryResponse:
    return InvestigationQueryResponse(
        payment_id=payment_id,
        question=question,
        root_cause=rca.root_cause,
        confidence=rca.normalized_confidence(),
        evidence=rca.evidence,
        recommendation=rca.recommendation,
        sources=rca.sources,
        answer=rca.to_answer(),
        steps=steps,
        model=model,
        provider=provider,
    )
