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


class PaymentEventListResponse(BaseModel):
    items: list[PaymentEventRead]


class PaymentLogListResponse(BaseModel):
    items: list[PaymentLogRead]


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


class DocumentationSourceReference(BaseModel):
    document_id: int
    document_name: str
    category: str
    section_heading: str | None = None
    chunk_index: int | None = None


class PaymentDocSearchResult(BaseModel):
    chunk_id: int
    content: str
    similarity: float
    source: DocumentationSourceReference


class InvestigationQueryRequest(BaseModel):
    payment_id: str = Field(min_length=1)
    question: str = Field(min_length=1)


class ToolExecutionStep(BaseModel):
    tool: str
    arguments: dict[str, Any]
    result: Any


class InvestigationCreateRequest(BaseModel):
    payment_id: str = Field(min_length=1)
    question: str = Field(
        default="Why did this payment fail?",
        min_length=1,
    )


class InvestigationListResponse(BaseModel):
    items: list["InvestigationRead"]


class InvestigationQueryResponse(BaseModel):
    id: int | None = None
    payment_id: str
    question: str
    root_cause: str
    confidence: str
    evidence: list[str]
    recommendation: str
    sources: list[str]
    answer: str
    steps: list[ToolExecutionStep]
    model: str
    provider: str
    insufficient_evidence: bool = False


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
