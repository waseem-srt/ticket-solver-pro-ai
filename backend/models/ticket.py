from __future__ import annotations

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base


class Ticket(Base):
    __tablename__ = "tickets"

    ticket_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    priority: Mapped[str] = mapped_column(String(20), nullable=False, default="medium", index=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open", index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
    tags: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    source_dataset: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Relationships
    embeddings = relationship(
        "TicketEmbedding", back_populates="ticket", cascade="all, delete-orphan"
    )


class TicketEmbedding(Base):
    __tablename__ = "ticket_embeddings"

    ticket_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chroma_id: Mapped[str] = mapped_column(String(255), nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Relationships
    ticket = relationship("Ticket", back_populates="embeddings")
