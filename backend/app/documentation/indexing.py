from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.documentation.chunking import ChunkDraft, chunk_markdown
from app.embeddings.base import EmbeddingClient
from app.embeddings.factory import get_embedding_client
from app.models import Document, DocumentChunk


def index_documents(
    session: Session,
    documents: list[Document],
    *,
    client: EmbeddingClient | None = None,
) -> int:
    embedding_client = client or get_embedding_client()
    chunks = build_document_chunks(documents)
    if not chunks:
        return 0

    vectors = embedding_client.embed_documents([chunk.content for chunk in chunks])
    if len(vectors) != len(chunks):
        raise ValueError("Embedding client returned a mismatched number of vectors.")

    for chunk, vector in zip(chunks, vectors, strict=True):
        chunk.embedding = vector

    session.add_all(chunks)
    session.flush()
    return len(chunks)


def build_document_chunks(documents: list[Document]) -> list[DocumentChunk]:
    chunks: list[DocumentChunk] = []
    for document in documents:
        if document.id is None:
            raise ValueError("Document must be persisted before chunking.")
        for draft in chunk_document(document):
            chunks.append(
                DocumentChunk(
                    document_id=document.id,
                    content=draft.content,
                    chunk_metadata=draft.metadata,
                )
            )
    return chunks


def chunk_document(document: Document) -> list[ChunkDraft]:
    return chunk_markdown(
        document.content,
        document_name=document.name,
        category=document.category,
    )


def chunk_count(session: Session) -> int:
    return session.scalar(select(func.count()).select_from(DocumentChunk)) or 0
