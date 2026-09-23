from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class PaymentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    customer_id: str
    amount: Decimal
    currency: str
    payment_method: str
    status: str
    gateway: str
    error_code: str | None
    created_at: datetime
    updated_at: datetime


class PaymentListResponse(BaseModel):
    items: list[PaymentRead]


class PaymentEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    payment_id: str
    event_type: str
    status: str
    metadata: dict[str, Any] = Field(validation_alias="event_metadata")
    created_at: datetime


class PaymentLogRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    payment_id: str
    service: str
    level: str
    message: str
    metadata: dict[str, Any] = Field(validation_alias="log_metadata")
    created_at: datetime


class DocumentRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    content: str
    created_at: datetime


class InvestigationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    payment_id: str
    question: str
    root_cause: str | None
    evidence: list[Any]
    recommendation: str | None
    confidence: str | None
    created_at: datetime
