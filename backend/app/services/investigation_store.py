from app.api_errors import investigation_not_found, payment_not_found
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

    def require_payment(self, payment_id: str) -> None:
        if self._payments.get_by_id(payment_id) is None:
            raise payment_not_found(payment_id)

    def save(self, response: InvestigationQueryResponse) -> Investigation:
        self.require_payment(response.payment_id)
        return self._investigations.create_from_response(response)

    def get(self, investigation_id: int) -> Investigation:
        record = self._investigations.get_by_id(investigation_id)
        if record is None:
            raise investigation_not_found(investigation_id)
        return record

    def list_for_payment(self, payment_id: str, *, limit: int = 50) -> list[Investigation]:
        self.require_payment(payment_id)
        return self._investigations.list_for_payment(payment_id, limit=limit)
