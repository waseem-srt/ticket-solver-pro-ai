from __future__ import annotations

from functools import lru_cache

from chromadb.utils import embedding_functions

from core.config import settings


@lru_cache(maxsize=1)
def get_embedding_function():
    """
    Returns a ChromaDB-compatible BGE-small-en-v1.5 embedding function.
    Cached as a singleton to avoid re-loading the model on every call.
    """
    return embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=settings.embedding_model,
        normalize_embeddings=True,  # recommended for BGE models
    )
