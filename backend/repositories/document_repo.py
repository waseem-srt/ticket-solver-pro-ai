from __future__ import annotations

from typing import Any, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.document import Document, DocumentChunk


class DocumentRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(
        self,
        filename: str,
        source: str | None,
        content_type: str | None,
        uploaded_by: str | None,
        metadata: dict[str, Any] | None = None,
    ) -> Document:
        doc = Document(
            filename=filename,
            source=source,
            content_type=content_type,
            uploaded_by=str(uploaded_by) if uploaded_by else None,
            metadata_=metadata or {},
        )
        self.db.add(doc)
        await self.db.flush()
        await self.db.refresh(doc)
        return doc

    async def get_by_id(self, doc_id: str) -> Document | None:
        result = await self.db.execute(select(Document).where(Document.id == str(doc_id)))
        return result.scalars().first()

    async def list_documents(self, skip: int = 0, limit: int = 50) -> tuple[Sequence[Document], int]:
        total_result = await self.db.execute(select(func.count(Document.id)))
        total = total_result.scalar() or 0
        result = await self.db.execute(
            select(Document).offset(skip).limit(limit).order_by(Document.created_at.desc())
        )
        return result.scalars().all(), total

    async def delete(self, doc_id: str) -> bool:
        result = await self.db.execute(select(Document).where(Document.id == str(doc_id)))
        doc = result.scalars().first()
        if not doc:
            return False
        await self.db.delete(doc)
        await self.db.flush()
        return True

    # ── Chunks ───────────────────────────────────────────────────────────

    async def add_chunk(
        self,
        document_id: str,
        chroma_id: str,
        chunk_text: str,
        chunk_index: int,
        metadata: dict[str, Any] | None = None,
    ) -> DocumentChunk:
        chunk = DocumentChunk(
            document_id=str(document_id),
            chroma_id=chroma_id,
            chunk_text=chunk_text,
            chunk_index=chunk_index,
            metadata_=metadata or {},
        )
        self.db.add(chunk)
        await self.db.flush()
        return chunk
