from fastapi import HTTPException, status

from app.models import Payment
from app.repositories.payment import PaymentRepository


class PaymentService:
    def __init__(self, repository: PaymentRepository) -> None:
        self.repository = repository

    def list_payments(
        self,
        *,
        query: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> list[Payment]:
        return self.repository.list(query=query, status=status, limit=limit)

    def get_payment(self, payment_id: str) -> Payment:
        payment = self.repository.get_by_id(payment_id)
        if payment is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Payment {payment_id} was not found.",
            )
        return payment
