from __future__ import annotations

from dataclasses import dataclass, field

from core.config import settings
from vectorstore.chroma_store import get_chroma_store


@dataclass
class RetrievedChunk:
    text: str
    metadata: dict
    distance: float

    @property
    def is_confident(self) -> bool:
        """Cosine distance in ChromaDB: 0 = identical, 2 = opposite."""
        return self.distance <= (1.0 - settings.rag_confidence_threshold)


class RAGRetriever:
    """Queries ChromaDB ticket and document collections for relevant context."""

    def __init__(
        self,
        use_tickets: bool = True,
        use_documents: bool = True,
    ) -> None:
        self.store = get_chroma_store()
        self.use_tickets = use_tickets
        self.use_documents = use_documents

    def retrieve(
        self, query: str, n_results: int | None = None
    ) -> list[RetrievedChunk]:
        k = n_results or settings.rag_top_k
        results: list[RetrievedChunk] = []

        # Query tickets (only if enabled)
        if self.use_tickets:
            try:
                ticket_results = self.store.tickets_collection.query(
                    query_texts=[query],
                    n_results=k,
                    include=["documents", "metadatas", "distances"],
                )
                if ticket_results["documents"]:
                    for doc, meta, dist in zip(
                        ticket_results["documents"][0],
                        ticket_results["metadatas"][0],
                        ticket_results["distances"][0],
                    ):
                        results.append(RetrievedChunk(text=doc, metadata=meta, distance=dist))
            except Exception:
                pass  # Collection might be empty

        # Query documents (only if enabled)
        if self.use_documents:
            try:
                doc_results = self.store.documents_collection.query(
                    query_texts=[query],
                    n_results=max(1, k // 2),
                    include=["documents", "metadatas", "distances"],
                )
                if doc_results["documents"]:
                    for doc, meta, dist in zip(
                        doc_results["documents"][0],
                        doc_results["metadatas"][0],
                        doc_results["distances"][0],
                    ):
                        results.append(RetrievedChunk(text=doc, metadata=meta, distance=dist))
            except Exception:
                pass

        # Sort by relevance (lower distance = better)
        results.sort(key=lambda x: x.distance)
        return results[:k]

    def is_knowledge_base_empty(self) -> bool:
        try:
            tickets_empty = True
            documents_empty = True
            if self.use_tickets:
                tickets_empty = self.store.tickets_collection.count() == 0
            if self.use_documents:
                documents_empty = self.store.documents_collection.count() == 0
            return tickets_empty and documents_empty
        except Exception:
            return True
