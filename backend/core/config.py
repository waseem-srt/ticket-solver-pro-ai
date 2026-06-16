from __future__ import annotations

import os
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=[".env", ".env.local"],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────────────────────────
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8000
    cors_origins: str = "http://localhost:3000"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    # ── Database ─────────────────────────────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///./data/app.db"

    # ── JWT ──────────────────────────────────────────────────────────────
    jwt_secret_key: str = "CHANGE-ME-to-a-very-long-random-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # ── Admin ────────────────────────────────────────────────────────────
    admin_invite_code: str = "admin-secret-2025"

    # ── HuggingFace ──────────────────────────────────────────────────────
    hf_token: str = ""
    hf_model_repo: str = "Qwen/Qwen2.5-1.5B-Instruct"
    run_local_llm: bool = False

    # ── ChromaDB ─────────────────────────────────────────────────────────
    chroma_persist_dir: str = "./data/chromadb"
    chroma_tickets_collection: str = "ticket_knowledge_base"
    chroma_documents_collection: str = "document_knowledge_base"

    # ── Embeddings ───────────────────────────────────────────────────────
    embedding_model: str = "BAAI/bge-small-en-v1.5"

    # ── RAG ──────────────────────────────────────────────────────────────
    rag_top_k: int = 5
    rag_confidence_threshold: float = 0.4

    # ── Web Search ───────────────────────────────────────────────────────
    web_search_max_results: int = 5


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
