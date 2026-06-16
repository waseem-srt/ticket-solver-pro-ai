from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ChatSessionCreate(BaseModel):
    title: str = Field(default="New Chat", max_length=255)


class ChatSessionUpdate(BaseModel):
    title: str = Field(..., max_length=255)


class ChatSessionOut(BaseModel):
    id: str
    title: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    message_count: int = 0

    model_config = {"from_attributes": True}


class ChatMessageOut(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    citations: list[Any] = []
    confidence_score: float | None = None
    created_at: datetime

    model_config = {"from_attributes": True}


class ChatSessionDetail(ChatSessionOut):
    messages: list[ChatMessageOut] = []


class SendMessageRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=8000)
