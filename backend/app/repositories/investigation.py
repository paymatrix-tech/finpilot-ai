from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Investigation
from app.schemas import InvestigationQueryResponse


class InvestigationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_from_response(self, response: InvestigationQueryResponse) -> Investigation:
        record = Investigation(
            payment_id=response.payment_id,
            question=response.question,
            root_cause=response.root_cause,
            evidence=response.evidence,
            recommendation=response.recommendation,
            confidence=response.confidence,
        )
        self.session.add(record)
        self.session.flush()
        return record

    def get_by_id(self, investigation_id: int) -> Investigation | None:
        return self.session.get(Investigation, investigation_id)

    def list_for_payment(self, payment_id: str, *, limit: int = 50) -> list[Investigation]:
        statement = (
            select(Investigation)
            .where(Investigation.payment_id == payment_id)
            .order_by(Investigation.created_at.desc())
            .limit(limit)
        )
        return list(self.session.scalars(statement).all())
