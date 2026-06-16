from __future__ import annotations

from pydantic import BaseModel


class RAGDataSourceOut(BaseModel):
    id: str
    source_type: str
    enabled: bool
    created_at: str

    model_config = {"from_attributes": True}


class RAGDataSourceUpdate(BaseModel):
    enabled: bool


class RAGDataSourceListOut(BaseModel):
    sources: list[RAGDataSourceOut]


class CollectionStatsOut(BaseModel):
    tickets_count: int
    documents_count: int
    tickets_enabled: bool
    documents_enabled: bool
