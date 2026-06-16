from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class TicketOut(BaseModel):
    id: str
    ticket_number: str
    category: str | None
    priority: str
    status: str
    title: str
    description: str | None
    resolution: str | None
    tags: list[Any]
    source_dataset: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class TicketListOut(BaseModel):
    items: list[TicketOut]
    total: int
    page: int
    page_size: int


class TicketUploadResponse(BaseModel):
    inserted: int
    skipped: int
    errors: int
    message: str


class ReindexResponse(BaseModel):
    indexed: int
    message: str
