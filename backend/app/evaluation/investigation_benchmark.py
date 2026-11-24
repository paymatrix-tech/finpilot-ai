from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.documentation.seed import seed_documents
from app.llm.stub import StubLLMClient
from app.repositories.documentation import DocumentationRepository
from app.repositories.payment import PaymentRepository
from app.schemas import InvestigationQueryResponse
from app.services.investigation_agent import InvestigationAgent
from app.tools.documentation import DocumentationTools
from app.tools.executor import PaymentToolExecutor
from app.tools.payment import PaymentTools


@dataclass(frozen=True)
class InvestigationEvalCase:
    id: str
    question: str
    expected_root_cause: str
    expected_confidence: str | None = None


INVESTIGATION_EVAL_CASES: tuple[InvestigationEvalCase, ...] = (
    InvestigationEvalCase(
        id="ach-r01-failure",
        question="Why did this payment fail?",
        expected_root_cause="Insufficient funds",
        expected_confidence="high",
    ),
    InvestigationEvalCase(
        id="gateway-timeout",
        question="Why is this payment failed or stuck?",
        expected_root_cause="Gateway timeout",
        expected_confidence="medium",
    ),
)


def run_investigation_eval(
    db: Session,
    payment_id: str,
    case: InvestigationEvalCase,
    *,
    llm: StubLLMClient | None = None,
) -> InvestigationQueryResponse:
    seed_documents(db)
    payment_tools = PaymentTools(PaymentRepository(db))
    documentation_tools = DocumentationTools(DocumentationRepository(db))
    agent = InvestigationAgent(
        llm or StubLLMClient(),
        PaymentToolExecutor(payment_tools, documentation_tools),
    )
    return agent.investigate(payment_id, case.question)
