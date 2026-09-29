from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_session
from app.llm.base import LLMClient
from app.llm.exceptions import LLMConfigurationError, LLMRequestError
from app.llm.factory import get_llm_client
from app.repositories.payment import PaymentRepository
from app.schemas import InvestigationQueryRequest, InvestigationQueryResponse
from app.services.investigation_agent import InvestigationAgent
from app.tools.executor import PaymentToolExecutor
from app.tools.payment import PaymentTools

router = APIRouter(prefix="/api/investigations", tags=["investigations"])


def get_investigation_agent(
    session: Annotated[Session, Depends(get_session)],
    llm: Annotated[LLMClient, Depends(get_llm_client)],
) -> InvestigationAgent:
    tools = PaymentTools(PaymentRepository(session))
    return InvestigationAgent(llm, PaymentToolExecutor(tools))


@router.post("/query", response_model=InvestigationQueryResponse)
def investigate_payment(
    body: InvestigationQueryRequest,
    agent: Annotated[InvestigationAgent, Depends(get_investigation_agent)],
) -> InvestigationQueryResponse:
    try:
        return agent.investigate(body.payment_id, body.question)
    except LLMConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except LLMRequestError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
