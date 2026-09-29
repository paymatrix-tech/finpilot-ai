from app.repositories.payment import PaymentRepository
from app.schemas import PaymentEventRead, PaymentLogRead, PaymentRead
from app.tools.exceptions import PaymentNotFoundError


class PaymentTools:
    """Read-only investigation tools backed by payment data (Day 9)."""

    def __init__(self, repository: PaymentRepository) -> None:
        self._repository = repository

    def get_payment(self, payment_id: str) -> PaymentRead:
        payment = self._repository.get_by_id(payment_id)
        if payment is None:
            raise PaymentNotFoundError(payment_id)
        return PaymentRead.model_validate(payment)

    def get_payment_events(self, payment_id: str) -> list[PaymentEventRead]:
        self._ensure_payment_exists(payment_id)
        events = self._repository.list_events(payment_id)
        return [PaymentEventRead.model_validate(event) for event in events]

    def search_logs(
        self,
        payment_id: str,
        query: str | None = None,
        *,
        limit: int = 50,
    ) -> list[PaymentLogRead]:
        self._ensure_payment_exists(payment_id)
        logs = self._repository.search_logs(payment_id, query=query, limit=limit)
        return [PaymentLogRead.model_validate(log) for log in logs]

    def _ensure_payment_exists(self, payment_id: str) -> None:
        if self._repository.get_by_id(payment_id) is None:
            raise PaymentNotFoundError(payment_id)
