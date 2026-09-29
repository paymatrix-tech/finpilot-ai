from dataclasses import dataclass

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Document, DocumentChunk


@dataclass(frozen=True)
class DocumentChunkMatch:
    chunk: DocumentChunk
    document: Document
    distance: float


class DocumentationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def search_similar_chunks(
        self,
        query_embedding: list[float],
        *,
        limit: int = 5,
    ) -> list[DocumentChunkMatch]:
        if limit < 1:
            return []

        distance_expr = DocumentChunk.embedding.cosine_distance(query_embedding)
        statement = (
            select(DocumentChunk, Document, distance_expr.label("distance"))
            .join(Document, Document.id == DocumentChunk.document_id)
            .where(DocumentChunk.embedding.is_not(None))
            .order_by(distance_expr)
            .limit(limit)
        )
        rows = self.session.execute(statement).all()
        return [
            DocumentChunkMatch(
                chunk=chunk,
                document=document,
                distance=float(distance),
            )
            for chunk, document, distance in rows
        ]
