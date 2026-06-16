from __future__ import annotations

import logging
import os

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.router import api_router
from core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup: auto-create DB tables, initialize ChromaDB and embedding model."""
    logger.info("Starting Ticket Solver Pro AI...")

    # Ensure data directories exist
    os.makedirs("data/tickets", exist_ok=True)
    os.makedirs("data/documents", exist_ok=True)
    os.makedirs("data/exports", exist_ok=True)
    os.makedirs(settings.chroma_persist_dir, exist_ok=True)

    # Auto-create database tables
    from core.database import engine
    from models import Base  # noqa: F401 — ensures all models are registered
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created / verified.")

    # Seed default RAG data sources if not present
    from core.database import AsyncSessionFactory
    from sqlalchemy import select
    from models.rag_config import RAGDataSource
    async with AsyncSessionFactory() as session:
        result = await session.execute(select(RAGDataSource))
        existing = result.scalars().all()
        existing_types = {s.source_type for s in existing}
        for stype in ("tickets", "documents"):
            if stype not in existing_types:
                session.add(RAGDataSource(source_type=stype, enabled=True))
        await session.commit()
    logger.info("RAG data sources seeded.")

    # Pre-initialize ChromaDB and embedding model (loads BGE model)
    try:
        from vectorstore.chroma_store import get_chroma_store
        store = get_chroma_store()
        logger.info(
            f"ChromaDB ready — tickets: {store.tickets_collection.count()}, "
            f"documents: {store.documents_collection.count()}"
        )
    except Exception as e:
        logger.warning(f"ChromaDB initialization warning: {e}")

    logger.info(f"LLM model: {settings.hf_model_repo}")
    logger.info("API ready at http://localhost:8000/docs")
    yield
    logger.info("Shutting down...")


app = FastAPI(
    title="Ticket Solver Pro AI",
    description="RAG-powered support ticket analysis with LangGraph agents",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "model": settings.hf_model_repo}
