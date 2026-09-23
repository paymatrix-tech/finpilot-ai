from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_session
from app.models import Payment
from app.repositories.payment import PaymentRepository
from app.schemas import PaymentListResponse, PaymentRead
from app.services.payment import PaymentService

router = APIRouter(prefix="/api/payments", tags=["payments"])


def get_payment_service(session: Annotated[Session, Depends(get_session)]) -> PaymentService:
    return PaymentService(PaymentRepository(session))


@router.get("", response_model=PaymentListResponse)
def list_payments(
    service: Annotated[PaymentService, Depends(get_payment_service)],
    q: str | None = Query(default=None, description="Search by id, gateway, error code, or customer"),
    status: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
) -> PaymentListResponse:
    payments = service.list_payments(query=q, status=status, limit=limit)
    return PaymentListResponse(items=payments)


@router.get("/{payment_id}", response_model=PaymentRead)
def get_payment(
    payment_id: str,
    service: Annotated[PaymentService, Depends(get_payment_service)],
) -> Payment:
    return service.get_payment(payment_id)
