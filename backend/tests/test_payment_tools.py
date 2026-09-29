import pytest
from sqlalchemy.orm import Session

from app.models import Payment
from app.repositories.payment import PaymentRepository
from app.tools.exceptions import PaymentNotFoundError
from app.tools.payment import PaymentTools


@pytest.fixture
def payment_tools(db: Session) -> PaymentTools:
    return PaymentTools(PaymentRepository(db))


def test_get_payment_returns_core_fields(
    payment_tools: PaymentTools, sample_payments: list[Payment]
) -> None:
    payment_id = sample_payments[0].id
    result = payment_tools.get_payment(payment_id)

    assert result.id == payment_id
    assert result.status == "FAILED"
    assert result.gateway == "ExamplePay"
    assert result.error_code == "R01"
    assert str(result.amount) == "2450.00"
    assert result.currency == "USD"


def test_get_payment_not_found(payment_tools: PaymentTools) -> None:
    with pytest.raises(PaymentNotFoundError):
        payment_tools.get_payment("PAY-DOES-NOT-EXIST")


def test_get_payment_events_lifecycle(
    payment_tools: PaymentTools, sample_payments: list[Payment]
) -> None:
    payment_id = sample_payments[0].id
    events = payment_tools.get_payment_events(payment_id)

    assert len(events) == 3
    assert [event.event_type for event in events] == [
        "PAYMENT_CREATED",
        "VALIDATED",
        "GATEWAY_RESPONSE",
    ]
    assert events[-1].metadata == {"error_code": "R01"}


def test_get_payment_events_requires_payment(
    payment_tools: PaymentTools,
) -> None:
    with pytest.raises(PaymentNotFoundError):
        payment_tools.get_payment_events("PAY-DOES-NOT-EXIST")


def test_search_logs_filters_by_query(
    payment_tools: PaymentTools, sample_payments: list[Payment]
) -> None:
    payment_id = sample_payments[0].id

    all_logs = payment_tools.search_logs(payment_id)
    assert len(all_logs) == 2

    gateway_logs = payment_tools.search_logs(payment_id, "R01")
    assert len(gateway_logs) == 1
    assert "R01" in gateway_logs[0].message

    no_match = payment_tools.search_logs(payment_id, "stripe")
    assert no_match == []


def test_search_logs_requires_payment(payment_tools: PaymentTools) -> None:
    with pytest.raises(PaymentNotFoundError):
        payment_tools.search_logs("PAY-DOES-NOT-EXIST", "gateway")
