import json
import re
from typing import Any

from pydantic import BaseModel, Field, ValidationError, field_validator

from app.llm.base import LLMClient
from app.llm.exceptions import LLMRequestError
from app.llm.types import ChatCompletionRequest, ChatMessage
from app.prompts.investigation import RCA_JSON_MARKER, RCA_SYSTEM_PROMPT

RCA_SYSTEM_PROMPT_EXPORT = RCA_SYSTEM_PROMPT  # backwards compatibility for imports


class InvestigationRCA(BaseModel):
    root_cause: str = Field(min_length=1)
    confidence: str
    evidence: list[str] = Field(default_factory=list)
    recommendation: str = Field(min_length=1)
    sources: list[str] = Field(default_factory=list)

    @field_validator("evidence", "sources", mode="before")
    @classmethod
    def coerce_string_list(cls, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        return []

    def normalized_confidence(self) -> str:
        value = self.confidence.strip().lower()
        if value in {"low", "medium", "high"}:
            return value
        return "low" if "insufficient" in self.root_cause.lower() else "medium"

    def to_answer(self) -> str:
        parts = [f"Root cause: {self.root_cause}"]
        if self.evidence:
            parts.append("Evidence: " + "; ".join(self.evidence[:3]))
        parts.append(f"Recommendation: {self.recommendation}")
        return " ".join(parts)

    def has_insufficient_evidence(self) -> bool:
        if "insufficient evidence" in self.root_cause.lower():
            return True
        if self.normalized_confidence() == "low" and len(self.evidence) == 0:
            return True
        return False


def generate_structured_rca(
    llm: LLMClient,
    messages: list[ChatMessage],
    *,
    payment_id: str,
    question: str,
) -> tuple[InvestigationRCA, str, str]:
    rca_messages = [
        ChatMessage(role="system", content=RCA_SYSTEM_PROMPT),
        *messages[1:],
        ChatMessage(
            role="user",
            content=(
                f"Payment ID: {payment_id}\n"
                f"Question: {question}\n"
                "Summarize only from tool results above. "
                "Include at least two evidence bullets when confidence is high.\n"
                f"{RCA_JSON_MARKER}"
            ),
        ),
    ]
    result = llm.complete(ChatCompletionRequest(messages=rca_messages, temperature=0.2))
    return parse_rca_response(result.content), result.model, result.provider


def parse_rca_response(raw: str) -> InvestigationRCA:
    payload = _extract_json_object(raw)
    try:
        rca = InvestigationRCA.model_validate(payload)
    except ValidationError as exc:
        raise LLMRequestError(f"RCA JSON did not match schema: {exc}") from exc

    return InvestigationRCA(
        root_cause=rca.root_cause.strip(),
        confidence=rca.normalized_confidence(),
        evidence=[item.strip() for item in rca.evidence if item.strip()],
        recommendation=rca.recommendation.strip(),
        sources=[item.strip() for item in rca.sources if item.strip()],
    )


def _extract_json_object(raw: str) -> dict[str, Any]:
    text = raw.strip()
    if not text:
        raise LLMRequestError("RCA response was empty.")

    fence_match = re.search(r"```(?:json)?\s*(\{.*\})\s*```", text, re.DOTALL)
    if fence_match:
        text = fence_match.group(1).strip()

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            raise LLMRequestError("RCA response did not contain JSON.") from None
        try:
            parsed = json.loads(text[start : end + 1])
        except json.JSONDecodeError as exc:
            raise LLMRequestError("RCA response was not valid JSON.") from exc

    if not isinstance(parsed, dict):
        raise LLMRequestError("RCA JSON must be an object.")
    return parsed
