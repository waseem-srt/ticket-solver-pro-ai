from __future__ import annotations

from fastapi import APIRouter, Query, UploadFile, File

from core.dependencies import AdminUser, DB
from schemas.ticket import (
    ReindexResponse,
    TicketListOut,
    TicketOut,
    TicketUploadResponse,
)
from services.ticket_service import TicketService

router = APIRouter(prefix="/tickets", tags=["Tickets"])


@router.get("", response_model=TicketListOut)
async def list_tickets(
    _: AdminUser,
    db: DB,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    category: str | None = Query(default=None),
    priority: str | None = Query(default=None),
    status: str | None = Query(default=None),
):
    svc = TicketService(db)
    tickets, total, pg, ps = await svc.list_tickets(
        page=page, page_size=page_size,
        category=category, priority=priority, status_filter=status
    )
    return {"items": tickets, "total": total, "page": pg, "page_size": ps}


@router.get("/{ticket_id}", response_model=TicketOut)
async def get_ticket(_: AdminUser, db: DB, ticket_id: str):
    svc = TicketService(db)
    return await svc.get_ticket(ticket_id)


@router.post("/upload", response_model=TicketUploadResponse, status_code=201)
async def upload_tickets(
    _: AdminUser,
    db: DB,
    file: UploadFile = File(..., description="CSV file with ticket data"),
):
    svc = TicketService(db)
    result = await svc.upload_csv(file)
    return {**result, "message": f"Ingested {result['inserted']} tickets"}


@router.post("/reindex", response_model=ReindexResponse)
async def reindex_tickets(_: AdminUser, db: DB):
    svc = TicketService(db)
    indexed = await svc.reindex_all()
    return {"indexed": indexed, "message": f"Re-indexed {indexed} tickets into ChromaDB"}
