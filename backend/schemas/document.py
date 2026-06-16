from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class DocumentOut(BaseModel):
    id: str
    filename: str
    source: str | None
    content_type: str | None
    metadata_: dict[str, Any] = {}
    created_at: datetime

    model_config = {"from_attributes": True, "populate_by_name": True}


class DocumentListOut(BaseModel):
    items: list[DocumentOut]
    total: int


class DocumentUploadResponse(BaseModel):
    id: str
    filename: str
    chunks_indexed: int
    message: str
