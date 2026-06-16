from __future__ import annotations

import os
from functools import lru_cache

import chromadb

from core.config import settings
from embeddings.embedding_service import get_embedding_function


class ChromaStore:
    """
    Manages ChromaDB persistent client and both collections
    (ticket_knowledge_base and document_knowledge_base).
    """

    def __init__(self) -> None:
        os.makedirs(settings.chroma_persist_dir, exist_ok=True)
        self._client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        ef = get_embedding_function()

        self.tickets_collection = self._client.get_or_create_collection(
            name=settings.chroma_tickets_collection,
            embedding_function=ef,
            metadata={"hnsw:space": "cosine"},
        )

        self.documents_collection = self._client.get_or_create_collection(
            name=settings.chroma_documents_collection,
            embedding_function=ef,
            metadata={"hnsw:space": "cosine"},
        )

    def reset_tickets(self) -> None:
        """Drop and recreate the tickets collection."""
        self._client.delete_collection(settings.chroma_tickets_collection)
        ef = get_embedding_function()
        self.tickets_collection = self._client.get_or_create_collection(
            name=settings.chroma_tickets_collection,
            embedding_function=ef,
            metadata={"hnsw:space": "cosine"},
        )

    def reset_documents(self) -> None:
        """Drop and recreate the documents collection."""
        self._client.delete_collection(settings.chroma_documents_collection)
        ef = get_embedding_function()
        self.documents_collection = self._client.get_or_create_collection(
            name=settings.chroma_documents_collection,
            embedding_function=ef,
            metadata={"hnsw:space": "cosine"},
        )

    @property
    def client(self) -> chromadb.PersistentClient:
        return self._client


@lru_cache(maxsize=1)
def get_chroma_store() -> ChromaStore:
    return ChromaStore()
