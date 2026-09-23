from datetime import timedelta

from app.seed import (
    CASE_IDS,
    OUTAGE_IDS,
    OUTAGE_START,
    build_seed_payments,
    designed_cases,
)


def test_designed_case_insufficient_funds() -> None:
    payment = next(item for item in designed_cases() if item.id == CASE_IDS["insufficient_funds"])
    assert payment.status == "FAILED"
    assert payment.error_code == "R01"
    assert payment.amount == payment.amount.__class__("2450.00")
    assert any(event.event_type == "GATEWAY_RESPONSE" for event in payment.events)
    assert any("R01" in log.message for log in payment.logs)
    assert not any("application error" in log.message.lower() for log in payment.logs)


def test_designed_case_gateway_timeout_has_no_gateway_response() -> None:
    payment = next(item for item in designed_cases() if item.id == CASE_IDS["gateway_timeout"])
    assert payment.error_code == "TIMEOUT"
    assert all(event.event_type != "GATEWAY_RESPONSE" for event in payment.events)
    assert any("timeout" in log.message.lower() for log in payment.logs)


def test_designed_case_application_error_never_calls_gateway() -> None:
    payment = next(item for item in designed_cases() if item.id == CASE_IDS["application_error"])
    assert payment.error_code == "APP_ERROR"
    event_types = {event.event_type for event in payment.events}
    assert "GATEWAY_REQUEST" not in event_types
    assert any("database" in log.message.lower() for log in payment.logs)


def test_designed_case_outage_cluster_shares_a_window() -> None:
    outage_payments = [item for item in designed_cases() if item.id in OUTAGE_IDS]
    assert len(outage_payments) == 15
    assert all(item.error_code == "GATEWAY_UNAVAILABLE" for item in outage_payments)
    timestamps = [item.created_at for item in outage_payments]
    assert min(timestamps) >= OUTAGE_START
    assert max(timestamps) - min(timestamps) < timedelta(minutes=10)


def test_seed_includes_required_failure_types() -> None:
    payments = build_seed_payments(250)
    assert len(payments) == 250
    codes = {item.error_code for item in payments}
    statuses = {item.status for item in payments}
    assert "SUCCESS" in statuses
    assert {"R01", "R03", "TIMEOUT", "05", "R67", "GATEWAY_ERROR", "GATEWAY_UNAVAILABLE"} <= codes
