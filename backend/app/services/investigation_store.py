from fastapi import HTTPException, status

from app.models import Investigation
from app.repositories.investigation import InvestigationRepository
from app.repositories.payment import PaymentRepository
from app.schemas import InvestigationQueryResponse


class InvestigationStoreService:
    def __init__(
        self,
        investigation_repository: InvestigationRepository,
        payment_repository: PaymentRepository,
    ) -> None:
        self._investigations = investigation_repository
        self._payments = payment_repository

    def save(self, response: InvestigationQueryResponse) -> Investigation:
        if self._payments.get_by_id(response.payment_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment {response.payment_id} was not found.",
            )
        return self._investigations.create_from_response(response)

    def get(self, investigation_id: int) -> Investigation:
        record = self._investigations.get_by_id(investigation_id)
        if record is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Investigation {investigation_id} was not found.",
            )
        return record

    def list_for_payment(self, payment_id: str, *, limit: int = 50) -> list[Investigation]:
        if self._payments.get_by_id(payment_id) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment {payment_id} was not found.",
            )
        return self._investigations.list_for_payment(payment_id, limit=limit)
