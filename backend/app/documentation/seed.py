from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from app.documentation.indexing import index_documents
from app.documentation.loader import iter_documentation_files, load_markdown_documents
from app.models import Document, DocumentChunk


def seed_documents(session: Session, *, reset: bool = True) -> int:
    expected_files = iter_documentation_files()
    if not expected_files:
        raise FileNotFoundError("No markdown files found in docs/.")

    if reset:
        session.execute(delete(DocumentChunk))
        session.execute(delete(Document))
        session.flush()

    documents = load_markdown_documents()
    session.add_all(documents)
    session.flush()
    index_documents(session, documents)
    session.commit()
    return len(documents)


def document_count(session: Session) -> int:
    return len(session.scalars(select(Document.id)).all())
