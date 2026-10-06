from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from app.documentation.loader import DOCUMENTATION_DIR
from app.schemas import PaymentDocSearchResult
from app.tools.documentation import DocumentationTools

DEFAULT_RETRIEVAL_LIMIT = 10


@dataclass(frozen=True)
class RagEvalCase:
    """Known question with gold document and answer terms for RAG evaluation."""

    id: str
    question: str
    search_query: str
    gold_document: str
    answer_terms: tuple[str, ...]
    retrieval_limit: int = DEFAULT_RETRIEVAL_LIMIT

    def validate_ground_truth(self) -> None:
        path = DOCUMENTATION_DIR / self.gold_document
        if not path.is_file():
            raise ValueError(f"Gold document missing: {self.gold_document}")
        content = path.read_text(encoding="utf-8").lower()
        missing = [term for term in self.answer_terms if term.lower() not in content]
        if missing:
            raise ValueError(
                f"Case {self.id}: answer terms not in {self.gold_document}: {missing}"
            )


@dataclass(frozen=True)
class RagEvalResult:
    case_id: str
    retrieved_documents: tuple[str, ...]
    matched_answer_terms: tuple[str, ...]
    gold_document_retrieved: bool

    @property
    def retrieval_passed(self) -> bool:
        return self.gold_document_retrieved

    @property
    def answer_passed(self) -> bool:
        return len(self.matched_answer_terms) >= 1

    @property
    def passed(self) -> bool:
        return self.retrieval_passed and self.answer_passed


def evaluate_rag_case(
    tools: DocumentationTools,
    case: RagEvalCase,
) -> RagEvalResult:
    case.validate_ground_truth()
    results = tools.search_payment_docs(case.search_query, limit=case.retrieval_limit)
    return _score_results(case, results)


def _score_results(case: RagEvalCase, results: list[PaymentDocSearchResult]) -> RagEvalResult:
    retrieved_documents = tuple(result.source.document_name for result in results)
    combined = "\n".join(result.content for result in results).lower()
    matched = tuple(term for term in case.answer_terms if term.lower() in combined)
    gold_document_retrieved = case.gold_document in set(retrieved_documents)
    return RagEvalResult(
        case_id=case.id,
        retrieved_documents=retrieved_documents,
        matched_answer_terms=matched,
        gold_document_retrieved=gold_document_retrieved,
    )


# Tuned for stub embeddings in CI; search_query may differ from natural question.
RAG_EVAL_CASES: tuple[RagEvalCase, ...] = (
    RagEvalCase(
        id="r01",
        question="What does R01 mean?",
        search_query="ach-error-codes.md",
        gold_document="ach-error-codes.md",
        answer_terms=("Insufficient funds", "R01"),
    ),
    RagEvalCase(
        id="r02",
        question="What does R02 mean?",
        search_query="ach-error-codes.md",
        gold_document="ach-error-codes.md",
        answer_terms=("Account closed", "R02"),
    ),
    RagEvalCase(
        id="r03",
        question="What does R03 mean?",
        search_query="ach-error-codes.md",
        gold_document="ach-error-codes.md",
        answer_terms=("R03", "No account"),
    ),
    RagEvalCase(
        id="retry-timeout",
        question="How should we retry gateway timeouts?",
        search_query="504 backoff",
        gold_document="retry-policy.md",
        answer_terms=("504", "backoff"),
    ),
    RagEvalCase(
        id="no-retry-r01",
        question="When should we not retry an ACH R01?",
        search_query="When not to retry R01?",
        gold_document="retry-policy.md",
        answer_terms=("R01", "2 business days"),
    ),
    RagEvalCase(
        id="processing-error",
        question="Is processing_error retryable for cards?",
        search_query="Retry processing_error? card-decline-codes",
        gold_document="card-decline-codes.md",
        answer_terms=("processing_error",),
    ),
    RagEvalCase(
        id="do-not-honor",
        question="Should we immediately retry do_not_honor?",
        search_query="do_not_honor",
        gold_document="card-decline-codes.md",
        answer_terms=("do_not_honor",),
    ),
    RagEvalCase(
        id="expired-card",
        question="What should we do for expired_card?",
        search_query="expired_card No — update card",
        gold_document="card-decline-codes.md",
        answer_terms=("expired_card",),
    ),
    RagEvalCase(
        id="gateway-503",
        question="How do we handle ExamplePay 503 outages?",
        search_query="503 service_unavailable",
        gold_document="gateway-runbook.md",
        answer_terms=("503", "service_unavailable"),
    ),
    RagEvalCase(
        id="gateway-timeout-symptoms",
        question="What are timeout symptoms in the runbook?",
        search_query="gateway-runbook.md",
        gold_document="gateway-runbook.md",
        answer_terms=("read timeout", "PROCESSING"),
    ),
    RagEvalCase(
        id="timeout-reconciliation",
        question="When does reconciliation poll stale PROCESSING payments?",
        search_query="timeout-handling.md",
        gold_document="timeout-handling.md",
        answer_terms=("reconciliation-worker", "15 minutes"),
    ),
    RagEvalCase(
        id="timeout-detection",
        question="How are timeouts detected in logs?",
        search_query="How to detect timeouts?",
        gold_document="timeout-handling.md",
        answer_terms=("deadline exceeded", "30 seconds"),
    ),
    RagEvalCase(
        id="lifecycle-events",
        question="What is the typical gateway event order?",
        search_query="4. `GATEWAY_RESPONSE` — final or interim gateway outcome.",
        gold_document="payment-processing.md",
        answer_terms=("GATEWAY_RESPONSE",),
    ),
    RagEvalCase(
        id="pay-1001-pattern",
        question="What failure pattern does PAY-1001 represent?",
        search_query="| PAY-1001 | ACH R01 insufficient funds | payment-processing",
        gold_document="payment-processing.md",
        answer_terms=("PAY-1001",),
    ),
    RagEvalCase(
        id="sev1",
        question="What qualifies as SEV1?",
        search_query="15 min incident-basics.md",
        gold_document="incident-basics.md",
        answer_terms=("SEV1",),
    ),
    RagEvalCase(
        id="sev2",
        question="What qualifies as SEV2?",
        search_query="SEV2 5%",
        gold_document="incident-basics.md",
        answer_terms=("SEV2", "5%"),
    ),
    RagEvalCase(
        id="incident-evidence",
        question="What evidence should we collect for payment RCA?",
        search_query="RCA evidence to collect?",
        gold_document="incident-basics.md",
        answer_terms=("error_code", "GATEWAY_RESPONSE"),
    ),
    RagEvalCase(
        id="gateway-decline-mapping",
        question="Where do decline codes land in our schema?",
        search_query="decline_code payments.error_code gateway-runbook",
        gold_document="gateway-runbook.md",
        answer_terms=("decline_code", "error_code"),
    ),
)


def load_gold_document_text(document_name: str) -> str:
    path = Path(DOCUMENTATION_DIR) / document_name
    return path.read_text(encoding="utf-8")
