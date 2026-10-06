"""Print a short RAG evaluation report (Day 23). Run from repo root:

    cd backend && python -m app.evaluation.run_rag_eval
"""

from __future__ import annotations

from app.db import SessionLocal
from app.documentation.seed import seed_documents
from app.evaluation.rag_benchmark import RAG_EVAL_CASES, evaluate_rag_case
from app.repositories.documentation import DocumentationRepository
from app.tools.documentation import DocumentationTools


def main() -> None:
    session = SessionLocal()
    try:
        seed_documents(session)
        tools = DocumentationTools(DocumentationRepository(session))
        passed = 0
        for case in RAG_EVAL_CASES:
            result = evaluate_rag_case(tools, case)
            status = "PASS" if result.passed else "FAIL"
            if result.passed:
                passed += 1
            print(
                f"{status}  {case.id:24}  Q: {case.question[:50]!r}  "
                f"docs={result.retrieved_documents[:3]}  terms={result.matched_answer_terms}"
            )
        print(f"\n{passed}/{len(RAG_EVAL_CASES)} cases passed.")
    finally:
        session.close()


if __name__ == "__main__":
    main()
