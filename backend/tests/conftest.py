from collections.abc import Generator
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.main import app
from app.models import Payment

TEST_PREFIX = "PAY-TEST-"


@pytest.fixture
def db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def sample_payments(db: Session) -> Generator[list[Payment], None, None]:
    payments = [
        Payment(
            id=f"{TEST_PREFIX}1001",
            customer_id="CUS-TEST-1",
            amount=Decimal("2450.00"),
            currency="USD",
            payment_method="ACH",
            status="FAILED",
            gateway="ExamplePay",
            error_code="R01",
        ),
        Payment(
            id=f"{TEST_PREFIX}1002",
            customer_id="CUS-TEST-2",
            amount=Decimal("800.00"),
            currency="USD",
            payment_method="CARD",
            status="SUCCESS",
            gateway="ExamplePay",
            error_code=None,
        ),
    ]
    db.add_all(payments)
    db.commit()
    for payment in payments:
        db.refresh(payment)

    try:
        yield payments
    finally:
        db.query(Payment).filter(Payment.id.startswith(TEST_PREFIX)).delete(
            synchronize_session=False
        )
        db.commit()
