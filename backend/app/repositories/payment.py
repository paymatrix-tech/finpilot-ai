from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models import Payment, PaymentEvent, PaymentLog
from app.security.sql import escape_like_pattern
from app.security.validation import MAX_PAYMENT_LIST_QUERY_LENGTH


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
            safe = escape_like_pattern(query[:MAX_PAYMENT_LIST_QUERY_LENGTH])
            pattern = f"%{safe}%"
            statement = statement.where(
                or_(
                    Payment.id.ilike(pattern, escape="\\"),
                    Payment.gateway.ilike(pattern, escape="\\"),
                    Payment.error_code.ilike(pattern, escape="\\"),
                    Payment.customer_id.ilike(pattern, escape="\\"),
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
            safe = escape_like_pattern(query.strip()[:500])
            pattern = f"%{safe}%"
            statement = statement.where(
                or_(
                    PaymentLog.message.ilike(pattern, escape="\\"),
                    PaymentLog.service.ilike(pattern, escape="\\"),
                    PaymentLog.level.ilike(pattern, escape="\\"),
                )
            )

        statement = statement.order_by(PaymentLog.created_at.asc()).limit(limit)
        return list(self.session.scalars(statement).all())

    def add(self, payment: Payment) -> Payment:
        self.session.add(payment)
        return payment
