from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select, update

from core.dependencies import AdminUser, DB
from models.rag_config import RAGDataSource
from schemas.rag_config import (
    CollectionStatsOut,
    RAGDataSourceListOut,
    RAGDataSourceOut,
    RAGDataSourceUpdate,
)

router = APIRouter(prefix="/admin/rag", tags=["Admin - RAG Config"])


@router.get("/sources", response_model=RAGDataSourceListOut)
async def list_rag_sources(_: AdminUser, db: DB):
    """List all RAG data sources and their enabled/disabled status."""
    result = await db.execute(select(RAGDataSource))
    sources = result.scalars().all()
    return {
        "sources": [
            RAGDataSourceOut(
                id=str(s.id),
                source_type=s.source_type,
                enabled=s.enabled,
                created_at=s.created_at.isoformat() if s.created_at else "",
            )
            for s in sources
        ]
    }


@router.put("/sources/{source_type}", response_model=RAGDataSourceOut)
async def update_rag_source(
    source_type: str,
    body: RAGDataSourceUpdate,
    current_user: AdminUser,
    db: DB,
):
    """Enable or disable a RAG data source (tickets or documents)."""
    if source_type not in ("tickets", "documents"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="source_type must be 'tickets' or 'documents'",
        )
    result = await db.execute(
        select(RAGDataSource).where(RAGDataSource.source_type == source_type)
    )
    source = result.scalars().first()
    if not source:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Data source '{source_type}' not found",
        )
    await db.execute(
        update(RAGDataSource)
        .where(RAGDataSource.source_type == source_type)
        .values(enabled=body.enabled, updated_by=str(current_user.id))
    )
    await db.flush()
    # Refresh
    result = await db.execute(
        select(RAGDataSource).where(RAGDataSource.source_type == source_type)
    )
    updated = result.scalars().first()
    return RAGDataSourceOut(
        id=str(updated.id),
        source_type=updated.source_type,
        enabled=updated.enabled,
        created_at=updated.created_at.isoformat() if updated.created_at else "",
    )


@router.get("/stats", response_model=CollectionStatsOut)
async def get_collection_stats(_: AdminUser, db: DB):
    """Get ChromaDB collection statistics and enabled status."""
    # Get enabled status from DB
    result = await db.execute(select(RAGDataSource))
    sources = result.scalars().all()
    source_map = {s.source_type: s.enabled for s in sources}

    # Get ChromaDB counts
    tickets_count = 0
    documents_count = 0
    try:
        from vectorstore.chroma_store import get_chroma_store
        store = get_chroma_store()
        tickets_count = store.tickets_collection.count()
        documents_count = store.documents_collection.count()
    except Exception:
        pass

    return CollectionStatsOut(
        tickets_count=tickets_count,
        documents_count=documents_count,
        tickets_enabled=source_map.get("tickets", True),
        documents_enabled=source_map.get("documents", True),
    )
