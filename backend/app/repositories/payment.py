from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Payment


class PaymentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list(
        self,
        *,
        query: str | None = None,
        status: str | None = None,
        limit: int = 50,
    ) -> list[Payment]:
        statement = select(Payment).order_by(Payment.created_at.desc()).limit(limit)

        if status:
            statement = statement.where(Payment.status == status)

        if query:
            pattern = f"%{query}%"
            statement = statement.where(
                or_(
                    Payment.id.ilike(pattern),
                    Payment.gateway.ilike(pattern),
                    Payment.error_code.ilike(pattern),
                    Payment.customer_id.ilike(pattern),
                )
            )

        return list(self.session.scalars(statement).all())

    def get_by_id(self, payment_id: str) -> Payment | None:
        return self.session.get(Payment, payment_id)

    def add(self, payment: Payment) -> Payment:
        self.session.add(payment)
        return payment
