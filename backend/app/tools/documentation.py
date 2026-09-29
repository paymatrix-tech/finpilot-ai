from app.embeddings.base import EmbeddingClient
from app.embeddings.factory import get_embedding_client
from app.repositories.documentation import DocumentChunkMatch, DocumentationRepository
from app.schemas import DocumentationSourceReference, PaymentDocSearchResult
from app.tools.exceptions import ToolError


class DocumentationTools:
    """Semantic search over indexed payment operations documentation (Day 13)."""

    def __init__(
        self,
        repository: DocumentationRepository,
        *,
        embedding_client: EmbeddingClient | None = None,
    ) -> None:
        self._repository = repository
        self._embedding_client = embedding_client or get_embedding_client()

    def search_payment_docs(
        self,
        query: str,
        *,
        limit: int = 5,
    ) -> list[PaymentDocSearchResult]:
        normalized = query.strip()
        if not normalized:
            raise ToolError("search_payment_docs query is required and must be non-empty.")

        if limit < 1:
            raise ToolError("search_payment_docs limit must be at least 1.")

        query_vector = self._embedding_client.embed_documents([normalized])[0]
        matches = self._repository.search_similar_chunks(query_vector, limit=limit)
        return [_to_search_result(match) for match in matches]


def _to_search_result(match: DocumentChunkMatch) -> PaymentDocSearchResult:
    metadata = match.chunk.chunk_metadata or {}
    distance = match.distance
    similarity = max(0.0, min(1.0, 1.0 - distance))
    return PaymentDocSearchResult(
        chunk_id=match.chunk.id,
        content=match.chunk.content,
        similarity=round(similarity, 4),
        source=DocumentationSourceReference(
            document_id=match.document.id,
            document_name=match.document.name,
            category=match.document.category,
            section_heading=metadata.get("section_heading"),
            chunk_index=metadata.get("chunk_index"),
        ),
    )
