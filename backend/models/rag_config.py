from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class RAGDataSource(Base):
    """Tracks which data sources are enabled for RAG retrieval.
    
    source_type: 'tickets' or 'documents'
    enabled: whether this source feeds into RAG context
    updated_by: admin user id who last changed this setting
    """
    __tablename__ = "rag_data_sources"

    source_type: Mapped[str] = mapped_column(
        String(50), unique=True, nullable=False, index=True
    )
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    updated_by: Mapped[str | None] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
