from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db import get_session
from app.models import Payment
from app.repositories.investigation import InvestigationRepository
from app.repositories.payment import PaymentRepository
from app.schemas import (
    InvestigationListResponse,
    PaymentEventListResponse,
    PaymentListResponse,
    PaymentLogListResponse,
    PaymentRead,
)
from app.services.investigation_store import InvestigationStoreService
from app.services.payment import PaymentService

router = APIRouter(prefix="/api/payments", tags=["payments"])


def get_payment_service(session: Annotated[Session, Depends(get_session)]) -> PaymentService:
    return PaymentService(PaymentRepository(session))


def get_investigation_store(
    session: Annotated[Session, Depends(get_session)],
) -> InvestigationStoreService:
    return InvestigationStoreService(
        InvestigationRepository(session),
        PaymentRepository(session),
    )


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


@router.get("/{payment_id}/investigations", response_model=InvestigationListResponse)
def list_payment_investigations(
    payment_id: str,
    store: Annotated[InvestigationStoreService, Depends(get_investigation_store)],
    limit: int = Query(default=50, ge=1, le=200),
) -> InvestigationListResponse:
    items = store.list_for_payment(payment_id, limit=limit)
    return InvestigationListResponse(items=items)


@router.get("/{payment_id}/events", response_model=PaymentEventListResponse)
def list_payment_events(
    payment_id: str,
    service: Annotated[PaymentService, Depends(get_payment_service)],
) -> PaymentEventListResponse:
    events = service.get_payment_events(payment_id)
    return PaymentEventListResponse(items=events)


@router.get("/{payment_id}/logs", response_model=PaymentLogListResponse)
def list_payment_logs(
    payment_id: str,
    service: Annotated[PaymentService, Depends(get_payment_service)],
) -> PaymentLogListResponse:
    logs = service.get_payment_logs(payment_id)
    return PaymentLogListResponse(items=logs)
