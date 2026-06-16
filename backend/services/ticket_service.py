from __future__ import annotations

import io
import csv
import uuid
from typing import Any

from fastapi import HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from ingestion.ticket_loader import TicketLoader
from repositories.ticket_repo import TicketRepository
from vectorstore.chroma_store import get_chroma_store


class TicketService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = TicketRepository(db)

    async def list_tickets(
        self,
        page: int = 1,
        page_size: int = 20,
        category: str | None = None,
        priority: str | None = None,
        status_filter: str | None = None,
    ):
        skip = (page - 1) * page_size
        tickets, total = await self.repo.list_tickets(
            skip=skip, limit=page_size,
            category=category, priority=priority, status=status_filter
        )
        return tickets, total, page, page_size

    async def get_ticket(self, ticket_id: uuid.UUID):
        ticket = await self.repo.get_by_id(ticket_id)
        if not ticket:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
        return ticket

    async def upload_csv(self, file: UploadFile) -> dict[str, Any]:
        if not file.filename.endswith(".csv"):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Only CSV files are supported",
            )
        contents = await file.read()
        text = contents.decode("utf-8", errors="replace")
        loader = TicketLoader()
        records = loader.parse_csv(text, source_dataset=file.filename)

        inserted = await self.repo.bulk_create(records)
        skipped = len(records) - inserted
        return {"inserted": inserted, "skipped": skipped, "errors": 0}

    async def reindex_all(self) -> int:
        """Re-embed all tickets into ChromaDB. Returns count indexed."""
        tickets = await self.repo.get_all_for_indexing()
        store = get_chroma_store()
        collection = store.tickets_collection

        indexed = 0
        batch_docs, batch_ids, batch_metas = [], [], []

        for ticket in tickets:
            text = f"{ticket.title}\n{ticket.description or ''}\n{ticket.resolution or ''}"
            doc_id = f"ticket-{ticket.id}"
            meta = {
                "ticket_id": str(ticket.id),
                "ticket_number": ticket.ticket_number,
                "category": ticket.category or "",
                "priority": ticket.priority,
                "status": ticket.status,
            }
            batch_docs.append(text)
            batch_ids.append(doc_id)
            batch_metas.append(meta)
            indexed += 1

            # Upsert in batches of 100
            if len(batch_docs) >= 100:
                collection.upsert(documents=batch_docs, ids=batch_ids, metadatas=batch_metas)
                batch_docs, batch_ids, batch_metas = [], [], []

        if batch_docs:
            collection.upsert(documents=batch_docs, ids=batch_ids, metadatas=batch_metas)

        return indexed
