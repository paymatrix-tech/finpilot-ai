from collections.abc import Iterator
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.api_errors import (
    database_error,
    error_detail,
    llm_request_failed,
    llm_unavailable,
    parse_error_payload,
)
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
from app.services.investigation_sse import format_sse
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


def _investigation_event_stream(
    agent: InvestigationAgent,
    store: InvestigationStoreService,
    session: Session,
    payment_id: str,
    question: str,
) -> Iterator[str]:
    if not check_database():
        yield format_sse("error", error_detail("database_error", "The database is temporarily unavailable."))
        return

    try:
        store.require_payment(payment_id)
    except HTTPException as exc:
        code, message = parse_error_payload(exc.detail)
        yield format_sse(
            "error",
            error_detail(code or "payment_not_found", message),
        )
        return

    try:
        for event, payload in agent.investigate_with_events(payment_id, question):
            if event == "complete":
                response = InvestigationQueryResponse.model_validate(payload)
                record = store.save(response)
                session.commit()
                session.refresh(record)
                payload = response.model_copy(update={"id": record.id}).model_dump(mode="json")
            yield format_sse(event, payload)
    except LLMConfigurationError as exc:
        yield format_sse(
            "error",
            error_detail("llm_unavailable", str(exc)),
        )
    except LLMRequestError as exc:
        yield format_sse(
            "error",
            error_detail("llm_request_failed", str(exc)),
        )
    except SQLAlchemyError:
        session.rollback()
        yield format_sse(
            "error",
            error_detail("database_error", "Could not reach the database. Try again in a moment."),
        )


@router.post("/stream")
def stream_investigation(
    body: InvestigationCreateRequest,
    agent: Annotated[InvestigationAgent, Depends(get_investigation_agent)],
    store: Annotated[InvestigationStoreService, Depends(get_investigation_store)],
    session: Annotated[Session, Depends(get_session)],
) -> StreamingResponse:
    generator = _investigation_event_stream(
        agent,
        store,
        session,
        body.payment_id,
        body.question,
    )
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


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
