from pathlib import Path

from app.models import Document

REPO_ROOT = Path(__file__).resolve().parents[3]
DOCUMENTATION_DIR = REPO_ROOT / "docs"

DOCUMENT_CATEGORIES: dict[str, str] = {
    "ach-error-codes.md": "errors",
    "card-decline-codes.md": "errors",
    "retry-policy.md": "policy",
    "gateway-runbook.md": "gateway",
    "payment-processing.md": "processing",
    "timeout-handling.md": "operations",
    "incident-basics.md": "operations",
}


def documentation_categories() -> dict[str, str]:
    return dict(DOCUMENT_CATEGORIES)


def iter_documentation_files() -> list[Path]:
    if not DOCUMENTATION_DIR.is_dir():
        return []
    return sorted(DOCUMENTATION_DIR.glob("*.md"))


def load_markdown_documents() -> list[Document]:
    documents: list[Document] = []
    for path in iter_documentation_files():
        name = path.name
        category = DOCUMENT_CATEGORIES.get(name, "general")
        content = path.read_text(encoding="utf-8").strip()
        if not content:
            raise ValueError(f"Documentation file {name} is empty.")
        documents.append(Document(name=name, category=category, content=content))
    return documents
