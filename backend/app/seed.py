from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from random import Random

from sqlalchemy import delete
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.documentation.seed import seed_documents
from app.models import Payment, PaymentEvent, PaymentLog

GATEWAY = "ExamplePay"
SEED_PREFIX = "PAY-"
TEST_PREFIX = "PAY-TEST-"
PAYMENT_COUNT = 250
OUTAGE_START = datetime(2026, 3, 14, 9, 4, tzinfo=timezone.utc)
CASE_IDS = {
    "insufficient_funds": "PAY-1001",
    "gateway_timeout": "PAY-1002",
    "application_error": "PAY-1003",
}
OUTAGE_IDS = [f"PAY-{n}" for n in range(1004, 1019)]


@dataclass
class Timeline:
    events: list[PaymentEvent]
    logs: list[PaymentLog]


def _ts(base: datetime, seconds: int) -> datetime:
    return base + timedelta(seconds=seconds)


def _event(
    payment_id: str,
    event_type: str,
    status: str,
    created_at: datetime,
    metadata: dict | None = None,
) -> PaymentEvent:
    return PaymentEvent(
        payment_id=payment_id,
        event_type=event_type,
        status=status,
        event_metadata=metadata or {},
        created_at=created_at,
    )


def _log(
    payment_id: str,
    message: str,
    created_at: datetime,
    *,
    service: str = "payments-api",
    level: str = "INFO",
    metadata: dict | None = None,
) -> PaymentLog:
    return PaymentLog(
        payment_id=payment_id,
        service=service,
        level=level,
        message=message,
        log_metadata=metadata or {},
        created_at=created_at,
    )


def _base_created_validated(payment_id: str, start: datetime) -> Timeline:
    return Timeline(
        events=[
            _event(payment_id, "PAYMENT_CREATED", "CREATED", _ts(start, 0)),
            _event(payment_id, "VALIDATED", "VALIDATED", _ts(start, 1)),
        ],
        logs=[
            _log(payment_id, "Payment accepted for processing", _ts(start, 0)),
            _log(payment_id, "Payment passed validation", _ts(start, 1)),
        ],
    )


def success_timeline(payment_id: str, start: datetime) -> Timeline:
    timeline = _base_created_validated(payment_id, start)
    timeline.events.extend(
        [
            _event(payment_id, "GATEWAY_REQUEST", "SUBMITTED", _ts(start, 2)),
            _event(
                payment_id,
                "GATEWAY_RESPONSE",
                "APPROVED",
                _ts(start, 3),
                {"result": "approved"},
            ),
            _event(payment_id, "PAYMENT_SUCCEEDED", "SUCCESS", _ts(start, 4)),
        ]
    )
    timeline.logs.extend(
        [
            _log(payment_id, "Sending payment to gateway", _ts(start, 2)),
            _log(payment_id, "Gateway approved the payment", _ts(start, 3)),
            _log(payment_id, "Marking payment as successful", _ts(start, 4)),
        ]
    )
    return timeline


def insufficient_funds_timeline(payment_id: str, start: datetime) -> Timeline:
    timeline = _base_created_validated(payment_id, start)
    timeline.events.extend(
        [
            _event(payment_id, "GATEWAY_REQUEST", "SUBMITTED", _ts(start, 2)),
            _event(
                payment_id,
                "GATEWAY_RESPONSE",
                "DECLINED",
                _ts(start, 3),
                {"error_code": "R01", "reason": "insufficient_funds"},
            ),
            _event(payment_id, "PAYMENT_FAILED", "FAILED", _ts(start, 3)),
        ]
    )
    timeline.logs.extend(
        [
            _log(payment_id, "Sending payment to gateway", _ts(start, 2)),
            _log(payment_id, "Gateway returned R01", _ts(start, 3), metadata={"error_code": "R01"}),
            _log(payment_id, "Marking payment as failed", _ts(start, 3)),
        ]
    )
    return timeline


def invalid_account_timeline(payment_id: str, start: datetime) -> Timeline:
    timeline = _base_created_validated(payment_id, start)
    timeline.events.extend(
        [
            _event(payment_id, "GATEWAY_REQUEST", "SUBMITTED", _ts(start, 2)),
            _event(
                payment_id,
                "GATEWAY_RESPONSE",
                "DECLINED",
                _ts(start, 3),
                {"error_code": "R03", "reason": "invalid_account"},
            ),
            _event(payment_id, "PAYMENT_FAILED", "FAILED", _ts(start, 3)),
        ]
    )
    timeline.logs.extend(
        [
            _log(payment_id, "Sending payment to gateway", _ts(start, 2)),
            _log(payment_id, "Gateway returned R03", _ts(start, 3), metadata={"error_code": "R03"}),
            _log(payment_id, "Marking payment as failed", _ts(start, 3)),
        ]
    )
    return timeline


def gateway_timeout_timeline(payment_id: str, start: datetime) -> Timeline:
    timeline = _base_created_validated(payment_id, start)
    timeline.events.extend(
        [
            _event(payment_id, "GATEWAY_REQUEST", "SUBMITTED", _ts(start, 2)),
            _event(payment_id, "PAYMENT_FAILED", "FAILED", _ts(start, 32), {"reason": "timeout"}),
        ]
    )
    timeline.logs.extend(
        [
            _log(payment_id, "Sending payment to gateway", _ts(start, 2)),
            _log(
                payment_id,
                "No gateway response received before timeout",
                _ts(start, 32),
                level="ERROR",
            ),
            _log(payment_id, "Marking payment as failed", _ts(start, 32)),
        ]
    )
    return timeline


def gateway_error_timeline(payment_id: str, start: datetime, *, outage: bool = False) -> Timeline:
    timeline = _base_created_validated(payment_id, start)
    metadata = {
        "http_status": 503,
        "error_code": "GATEWAY_UNAVAILABLE",
        "reason": "gateway_outage" if outage else "gateway_error",
    }
    timeline.events.extend(
        [
            _event(payment_id, "GATEWAY_REQUEST", "SUBMITTED", _ts(start, 2)),
            _event(payment_id, "GATEWAY_RESPONSE", "ERROR", _ts(start, 3), metadata),
            _event(payment_id, "PAYMENT_FAILED", "FAILED", _ts(start, 3)),
        ]
    )
    message = (
        "Gateway returned 503 Service Unavailable"
        if outage
        else "Gateway returned an unexpected error"
    )
    timeline.logs.extend(
        [
            _log(payment_id, "Sending payment to gateway", _ts(start, 2)),
            _log(payment_id, message, _ts(start, 3), level="ERROR", metadata=metadata),
            _log(payment_id, "Marking payment as failed", _ts(start, 3)),
        ]
    )
    return timeline


def card_decline_timeline(payment_id: str, start: datetime) -> Timeline:
    timeline = _base_created_validated(payment_id, start)
    timeline.events.extend(
        [
            _event(payment_id, "GATEWAY_REQUEST", "SUBMITTED", _ts(start, 2)),
            _event(
                payment_id,
                "GATEWAY_RESPONSE",
                "DECLINED",
                _ts(start, 3),
                {"error_code": "05", "reason": "card_declined"},
            ),
            _event(payment_id, "PAYMENT_FAILED", "FAILED", _ts(start, 3)),
        ]
    )
    timeline.logs.extend(
        [
            _log(payment_id, "Sending payment to gateway", _ts(start, 2)),
            _log(payment_id, "Gateway returned 05 do not honor", _ts(start, 3)),
            _log(payment_id, "Marking payment as failed", _ts(start, 3)),
        ]
    )
    return timeline


def duplicate_timeline(payment_id: str, start: datetime, original_id: str) -> Timeline:
    timeline = _base_created_validated(payment_id, start)
    timeline.events.extend(
        [
            _event(payment_id, "GATEWAY_REQUEST", "SUBMITTED", _ts(start, 2)),
            _event(
                payment_id,
                "GATEWAY_RESPONSE",
                "DECLINED",
                _ts(start, 3),
                {"error_code": "R67", "duplicate_of": original_id},
            ),
            _event(payment_id, "PAYMENT_FAILED", "FAILED", _ts(start, 3)),
        ]
    )
    timeline.logs.extend(
        [
            _log(payment_id, "Sending payment to gateway", _ts(start, 2)),
            _log(
                payment_id,
                f"Gateway returned R67 duplicate of {original_id}",
                _ts(start, 3),
                metadata={"duplicate_of": original_id},
            ),
            _log(payment_id, "Marking payment as failed", _ts(start, 3)),
        ]
    )
    return timeline


def application_error_timeline(payment_id: str, start: datetime) -> Timeline:
    timeline = _base_created_validated(payment_id, start)
    timeline.events.append(
        _event(
            payment_id,
            "PAYMENT_FAILED",
            "FAILED",
            _ts(start, 2),
            {"reason": "application_error"},
        )
    )
    timeline.logs.extend(
        [
            _log(
                payment_id,
                "Database connection failed while persisting gateway request",
                _ts(start, 2),
                service="payments-worker",
                level="ERROR",
                metadata={"error": "connection_refused"},
            ),
            _log(payment_id, "Marking payment as failed", _ts(start, 2), level="ERROR"),
        ]
    )
    return timeline


def build_payment(
    *,
    payment_id: str,
    customer_id: str,
    amount: Decimal,
    payment_method: str,
    status: str,
    error_code: str | None,
    start: datetime,
    timeline: Timeline,
) -> Payment:
    last_at = timeline.events[-1].created_at if timeline.events else start
    payment = Payment(
        id=payment_id,
        customer_id=customer_id,
        amount=amount,
        currency="USD",
        payment_method=payment_method,
        status=status,
        gateway=GATEWAY,
        error_code=error_code,
        created_at=start,
        updated_at=last_at,
    )
    payment.events = timeline.events
    payment.logs = timeline.logs
    return payment


def designed_cases() -> list[Payment]:
    case_1_start = datetime(2026, 3, 12, 14, 31, 52, tzinfo=timezone.utc)
    case_2_start = datetime(2026, 3, 13, 16, 10, 4, tzinfo=timezone.utc)
    case_3_start = datetime(2026, 3, 13, 18, 44, 11, tzinfo=timezone.utc)

    return [
        build_payment(
            payment_id=CASE_IDS["insufficient_funds"],
            customer_id="CUS-1001",
            amount=Decimal("2450.00"),
            payment_method="ACH",
            status="FAILED",
            error_code="R01",
            start=case_1_start,
            timeline=insufficient_funds_timeline(CASE_IDS["insufficient_funds"], case_1_start),
        ),
        build_payment(
            payment_id=CASE_IDS["gateway_timeout"],
            customer_id="CUS-1002",
            amount=Decimal("800.00"),
            payment_method="CARD",
            status="FAILED",
            error_code="TIMEOUT",
            start=case_2_start,
            timeline=gateway_timeout_timeline(CASE_IDS["gateway_timeout"], case_2_start),
        ),
        build_payment(
            payment_id=CASE_IDS["application_error"],
            customer_id="CUS-1003",
            amount=Decimal("120.00"),
            payment_method="ACH",
            status="FAILED",
            error_code="APP_ERROR",
            start=case_3_start,
            timeline=application_error_timeline(CASE_IDS["application_error"], case_3_start),
        ),
        *[
            build_payment(
                payment_id=payment_id,
                customer_id=f"CUS-{payment_id[-4:]}",
                amount=Decimal("95.00") + Decimal(index),
                payment_method="CARD",
                status="FAILED",
                error_code="GATEWAY_UNAVAILABLE",
                start=OUTAGE_START + timedelta(seconds=index * 20),
                timeline=gateway_error_timeline(
                    payment_id,
                    OUTAGE_START + timedelta(seconds=index * 20),
                    outage=True,
                ),
            )
            for index, payment_id in enumerate(OUTAGE_IDS)
        ],
    ]


def _scenario_for_index(index: int) -> str:
    bucket = index % 12
    if bucket <= 5:
        return "success"
    mapping = {
        6: "insufficient_funds",
        7: "invalid_account",
        8: "gateway_timeout",
        9: "card_decline",
        10: "duplicate",
        11: "gateway_error",
    }
    return mapping[bucket]


def leftover_payments(rng: Random, start_id: int, end_id: int) -> list[Payment]:
    payments: list[Payment] = []
    origin = datetime(2026, 3, 10, 12, 0, tzinfo=timezone.utc)

    for number in range(start_id, end_id + 1):
        payment_id = f"PAY-{number}"
        start = origin + timedelta(minutes=number)
        scenario = _scenario_for_index(number)
        customer_id = f"CUS-{number}"
        amount = Decimal(rng.randint(20, 5000)).quantize(Decimal("0.01"))

        if scenario == "success":
            payment = build_payment(
                payment_id=payment_id,
                customer_id=customer_id,
                amount=amount,
                payment_method="CARD" if number % 2 == 0 else "ACH",
                status="SUCCESS",
                error_code=None,
                start=start,
                timeline=success_timeline(payment_id, start),
            )
        elif scenario == "insufficient_funds":
            payment = build_payment(
                payment_id=payment_id,
                customer_id=customer_id,
                amount=amount,
                payment_method="ACH",
                status="FAILED",
                error_code="R01",
                start=start,
                timeline=insufficient_funds_timeline(payment_id, start),
            )
        elif scenario == "invalid_account":
            payment = build_payment(
                payment_id=payment_id,
                customer_id=customer_id,
                amount=amount,
                payment_method="ACH",
                status="FAILED",
                error_code="R03",
                start=start,
                timeline=invalid_account_timeline(payment_id, start),
            )
        elif scenario == "gateway_timeout":
            payment = build_payment(
                payment_id=payment_id,
                customer_id=customer_id,
                amount=amount,
                payment_method="CARD",
                status="FAILED",
                error_code="TIMEOUT",
                start=start,
                timeline=gateway_timeout_timeline(payment_id, start),
            )
        elif scenario == "card_decline":
            payment = build_payment(
                payment_id=payment_id,
                customer_id=customer_id,
                amount=amount,
                payment_method="CARD",
                status="FAILED",
                error_code="05",
                start=start,
                timeline=card_decline_timeline(payment_id, start),
            )
        elif scenario == "gateway_error":
            payment = build_payment(
                payment_id=payment_id,
                customer_id=customer_id,
                amount=amount,
                payment_method="CARD",
                status="FAILED",
                error_code="GATEWAY_ERROR",
                start=start,
                timeline=gateway_error_timeline(payment_id, start),
            )
        else:
            original_id = f"PAY-{max(start_id, number - 1)}"
            payment = build_payment(
                payment_id=payment_id,
                customer_id=customer_id,
                amount=amount,
                payment_method="ACH",
                status="FAILED",
                error_code="R67",
                start=start,
                timeline=duplicate_timeline(payment_id, start, original_id),
            )
        payments.append(payment)
    return payments


def build_seed_payments(count: int = PAYMENT_COUNT) -> list[Payment]:
    if count < 18:
        raise ValueError("Seed requires at least 18 payments for designed cases.")
    rng = Random(42)
    payments = designed_cases()
    remaining_start = 1019
    remaining_end = 1000 + count
    payments.extend(leftover_payments(rng, remaining_start, remaining_end))
    return payments


def clear_seed_payments(session: Session) -> None:
    session.execute(
        delete(Payment).where(
            Payment.id.startswith(SEED_PREFIX),
            ~Payment.id.startswith(TEST_PREFIX),
        )
    )


def seed_database(session: Session, *, count: int = PAYMENT_COUNT, reset: bool = True) -> int:
    if reset:
        clear_seed_payments(session)
        session.flush()
    payments = build_seed_payments(count)
    session.add_all(payments)
    session.commit()
    return len(payments)


def main() -> None:
    session = SessionLocal()
    try:
        created = seed_database(session)
        doc_count = seed_documents(session)
        print(f"Seeded {created} synthetic payments.")
        print(f"Loaded {doc_count} documentation files from docs/.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
