from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api_errors import database_error, llm_request_failed, llm_unavailable
from app.db import check_database, get_session
from app.llm.base import LLMClient
from app.llm.exceptions import LLMConfigurationError, LLMRequestError
from app.llm.factory import get_llm_client
from app.repositories.documentation import DocumentationRepository
from app.repositories.investigation import InvestigationRepository
from app.repositories.payment import PaymentRepository
from app.schemas import (
    InvestigationCreateRequest,
    InvestigationQueryRequest,
    InvestigationQueryResponse,
    InvestigationRead,
)
from app.services.investigation_agent import InvestigationAgent
from app.services.investigation_store import InvestigationStoreService
from app.tools.documentation import DocumentationTools
from app.tools.executor import PaymentToolExecutor
from app.tools.payment import PaymentTools

router = APIRouter(prefix="/api/investigations", tags=["investigations"])


def get_investigation_agent(
    session: Annotated[Session, Depends(get_session)],
    llm: Annotated[LLMClient, Depends(get_llm_client)],
) -> InvestigationAgent:
    payment_tools = PaymentTools(PaymentRepository(session))
    documentation_tools = DocumentationTools(DocumentationRepository(session))
    executor = PaymentToolExecutor(payment_tools, documentation_tools)
    return InvestigationAgent(llm, executor)


def get_investigation_store(
    session: Annotated[Session, Depends(get_session)],
) -> InvestigationStoreService:
    return InvestigationStoreService(
        InvestigationRepository(session),
        PaymentRepository(session),
    )


def _run_investigation(
    agent: InvestigationAgent,
    store: InvestigationStoreService,
    session: Session,
    payment_id: str,
    question: str,
) -> InvestigationQueryResponse:
    if not check_database():
        raise database_error()

    store.require_payment(payment_id)

    try:
        response = agent.investigate(payment_id, question)
    except LLMConfigurationError as exc:
        raise llm_unavailable(str(exc)) from exc
    except LLMRequestError as exc:
        raise llm_request_failed(str(exc)) from exc

    try:
        record = store.save(response)
        session.commit()
        session.refresh(record)
    except SQLAlchemyError as exc:
        session.rollback()
        raise database_error() from exc

    return response.model_copy(update={"id": record.id})


@router.get("/{investigation_id}", response_model=InvestigationRead)
def get_investigation(
    investigation_id: int,
    store: Annotated[InvestigationStoreService, Depends(get_investigation_store)],
) -> InvestigationRead:
    if not check_database():
        raise database_error()
    return store.get(investigation_id)


@router.post("", response_model=InvestigationQueryResponse)
def create_investigation(
    body: InvestigationCreateRequest,
    agent: Annotated[InvestigationAgent, Depends(get_investigation_agent)],
    store: Annotated[InvestigationStoreService, Depends(get_investigation_store)],
    session: Annotated[Session, Depends(get_session)],
) -> InvestigationQueryResponse:
    return _run_investigation(agent, store, session, body.payment_id, body.question)


@router.post("/query", response_model=InvestigationQueryResponse)
def investigate_payment(
    body: InvestigationQueryRequest,
    agent: Annotated[InvestigationAgent, Depends(get_investigation_agent)],
    store: Annotated[InvestigationStoreService, Depends(get_investigation_store)],
    session: Annotated[Session, Depends(get_session)],
) -> InvestigationQueryResponse:
    return _run_investigation(agent, store, session, body.payment_id, body.question)
