from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Payment, PaymentEvent, PaymentLog


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

    def list_events(self, payment_id: str) -> list[PaymentEvent]:
        statement = (
            select(PaymentEvent)
            .where(PaymentEvent.payment_id == payment_id)
            .order_by(PaymentEvent.created_at.asc())
        )
        return list(self.session.scalars(statement).all())

    def list_logs(self, payment_id: str) -> list[PaymentLog]:
        statement = (
            select(PaymentLog)
            .where(PaymentLog.payment_id == payment_id)
            .order_by(PaymentLog.created_at.asc())
        )
        return list(self.session.scalars(statement).all())

    def search_logs(
        self,
        payment_id: str,
        *,
        query: str | None = None,
        limit: int = 50,
    ) -> list[PaymentLog]:
        statement = select(PaymentLog).where(PaymentLog.payment_id == payment_id)

        if query:
            pattern = f"%{query.strip()}%"
            statement = statement.where(
                or_(
                    PaymentLog.message.ilike(pattern),
                    PaymentLog.service.ilike(pattern),
                    PaymentLog.level.ilike(pattern),
                )
            )

        statement = statement.order_by(PaymentLog.created_at.asc()).limit(limit)
        return list(self.session.scalars(statement).all())

    def add(self, payment: Payment) -> Payment:
        self.session.add(payment)
        return payment
