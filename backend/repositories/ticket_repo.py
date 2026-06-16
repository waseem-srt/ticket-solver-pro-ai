from __future__ import annotations

from typing import Any, Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models.ticket import Ticket, TicketEmbedding


class TicketRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, **kwargs) -> Ticket:
        ticket = Ticket(**kwargs)
        self.db.add(ticket)
        await self.db.flush()
        await self.db.refresh(ticket)
        return ticket

    async def bulk_create(self, tickets_data: list[dict[str, Any]]) -> int:
        """Insert many tickets; skip duplicates by ticket_number. Returns inserted count."""
        inserted = 0
        for data in tickets_data:
            existing = await self.get_by_number(data.get("ticket_number", ""))
            if existing:
                continue
            ticket = Ticket(**data)
            self.db.add(ticket)
            inserted += 1
        await self.db.flush()
        return inserted

    async def get_by_id(self, ticket_id: str) -> Ticket | None:
        result = await self.db.execute(select(Ticket).where(Ticket.id == str(ticket_id)))
        return result.scalars().first()

    async def get_by_number(self, ticket_number: str) -> Ticket | None:
        result = await self.db.execute(
            select(Ticket).where(Ticket.ticket_number == ticket_number)
        )
        return result.scalars().first()

    async def list_tickets(
        self,
        skip: int = 0,
        limit: int = 20,
        category: str | None = None,
        priority: str | None = None,
        status: str | None = None,
    ) -> tuple[Sequence[Ticket], int]:
        query = select(Ticket)
        if category:
            query = query.where(Ticket.category == category)
        if priority:
            query = query.where(Ticket.priority == priority)
        if status:
            query = query.where(Ticket.status == status)

        count_q = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_q)
        total = total_result.scalar() or 0

        result = await self.db.execute(query.offset(skip).limit(limit).order_by(Ticket.created_at.desc()))
        return result.scalars().all(), total

    async def get_all_for_indexing(self) -> Sequence[Ticket]:
        result = await self.db.execute(select(Ticket))
        return result.scalars().all()

    async def count(self) -> int:
        result = await self.db.execute(select(func.count(Ticket.id)))
        return result.scalar() or 0

    # ── Embeddings tracking ───────────────────────────────────────────────

    async def add_embedding(
        self, ticket_id: str, chroma_id: str, chunk_text: str, chunk_index: int = 0
    ) -> TicketEmbedding:
        emb = TicketEmbedding(
            ticket_id=str(ticket_id),
            chroma_id=chroma_id,
            chunk_text=chunk_text,
            chunk_index=chunk_index,
        )
        self.db.add(emb)
        await self.db.flush()
        return emb

    async def delete_ticket_embeddings(self, ticket_id: str) -> None:
        result = await self.db.execute(
            select(TicketEmbedding).where(TicketEmbedding.ticket_id == str(ticket_id))
        )
        for emb in result.scalars().all():
            await self.db.delete(emb)
        await self.db.flush()
