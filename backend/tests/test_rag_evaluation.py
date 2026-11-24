from decimal import Decimal

import pytest
from sqlalchemy.orm import Session

from app.evaluation.investigation_benchmark import INVESTIGATION_EVAL_CASES, run_investigation_eval
from app.evaluation.rag_benchmark import RAG_EVAL_CASES, evaluate_rag_case
from app.models import Payment, PaymentEvent, PaymentLog
from app.repositories.documentation import DocumentationRepository
from app.tools.documentation import DocumentationTools
from tests.conftest import TEST_PREFIX


@pytest.fixture
def documentation_tools(db: Session) -> DocumentationTools:
    from app.documentation.seed import seed_documents

    seed_documents(db)
    return DocumentationTools(DocumentationRepository(db))


@pytest.fixture
def timeout_payment(db: Session) -> Payment:
    payment = Payment(
        id=f"{TEST_PREFIX}2001",
        customer_id="CUS-TEST-TIMEOUT",
        amount=Decimal("1200.00"),
        currency="USD",
        payment_method="CARD",
        status="FAILED",
        gateway="ExamplePay",
        error_code="TIMEOUT",
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    db.add_all(
        [
            PaymentEvent(
                payment_id=payment.id,
                event_type="SUBMITTED",
                status="SUBMITTED",
            ),
            PaymentLog(
                payment_id=payment.id,
                service="payments-api",
                level="ERROR",
                message="Read timeout contacting ExamplePay gateway",
            ),
        ]
    )
    db.commit()
    try:
        yield payment
    finally:
        db.query(PaymentLog).filter(PaymentLog.payment_id == payment.id).delete(
            synchronize_session=False
        )
        db.query(PaymentEvent).filter(PaymentEvent.payment_id == payment.id).delete(
            synchronize_session=False
        )
        db.query(Payment).filter(Payment.id == payment.id).delete(synchronize_session=False)
        db.commit()


def test_rag_eval_dataset_has_expected_size() -> None:
    assert len(RAG_EVAL_CASES) >= 10


@pytest.mark.parametrize("case", RAG_EVAL_CASES, ids=lambda case: case.id)
def test_rag_eval_ground_truth(case) -> None:
    case.validate_ground_truth()


@pytest.mark.parametrize("case", RAG_EVAL_CASES, ids=lambda case: case.id)
def test_rag_eval_retrieval_and_answer(
    documentation_tools: DocumentationTools,
    case,
) -> None:
    result = evaluate_rag_case(documentation_tools, case)
    assert result.retrieval_passed, (
        f"Expected {case.gold_document} in top results, got {result.retrieved_documents}"
    )
    assert result.answer_passed, (
        f"Expected one of {case.answer_terms} in retrieved text, got {result.matched_answer_terms}"
    )


def test_investigation_eval_r01_case(
    db: Session,
    sample_payments: list[Payment],
) -> None:
    case = INVESTIGATION_EVAL_CASES[0]
    payment_id = sample_payments[0].id
    response = run_investigation_eval(db, payment_id, case)
    assert case.expected_root_cause in response.root_cause
    if case.expected_confidence:
        assert response.confidence == case.expected_confidence


def test_investigation_eval_timeout_case(db: Session, timeout_payment: Payment) -> None:
    case = INVESTIGATION_EVAL_CASES[1]
    response = run_investigation_eval(db, timeout_payment.id, case)
    assert case.expected_root_cause in response.root_cause
    if case.expected_confidence:
        assert response.confidence == case.expected_confidence
