from __future__ import annotations

from typing import Sequence

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from models.chat import ChatMessage, ChatSession


class ChatRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    # ── Sessions ─────────────────────────────────────────────────────────

    async def create_session(self, user_id: str, title: str = "New Chat") -> ChatSession:
        session = ChatSession(user_id=str(user_id), title=title)
        self.db.add(session)
        await self.db.flush()
        await self.db.refresh(session)
        return session

    async def get_session(self, session_id: str, user_id: str) -> ChatSession | None:
        result = await self.db.execute(
            select(ChatSession)
            .options(selectinload(ChatSession.messages))
            .where(ChatSession.id == str(session_id), ChatSession.user_id == str(user_id))
        )
        return result.scalars().first()

    async def list_sessions(self, user_id: str) -> Sequence[ChatSession]:
        result = await self.db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == str(user_id), ChatSession.is_active == True)  # noqa: E712
            .order_by(ChatSession.updated_at.desc())
        )
        return result.scalars().all()

    async def update_session_title(
        self, session_id: str, user_id: str, title: str
    ) -> ChatSession | None:
        await self.db.execute(
            update(ChatSession)
            .where(ChatSession.id == str(session_id), ChatSession.user_id == str(user_id))
            .values(title=title)
        )
        await self.db.flush()
        return await self.get_session(session_id, user_id)

    async def delete_session(self, session_id: str, user_id: str) -> bool:
        result = await self.db.execute(
            select(ChatSession).where(
                ChatSession.id == str(session_id), ChatSession.user_id == str(user_id)
            )
        )
        session = result.scalars().first()
        if not session:
            return False
        await self.db.delete(session)
        await self.db.flush()
        return True

    async def get_session_message_count(self, session_id: str) -> int:
        result = await self.db.execute(
            select(func.count(ChatMessage.id)).where(ChatMessage.session_id == str(session_id))
        )
        return result.scalar() or 0

    # ── Messages ─────────────────────────────────────────────────────────

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        citations: list | None = None,
        confidence_score: float | None = None,
        metadata: dict | None = None,
    ) -> ChatMessage:
        msg = ChatMessage(
            session_id=str(session_id),
            role=role,
            content=content,
            citations=citations or [],
            confidence_score=confidence_score,
            metadata_=metadata or {},
        )
        self.db.add(msg)
        await self.db.flush()
        await self.db.refresh(msg)
        return msg

    async def get_session_messages(self, session_id: str) -> Sequence[ChatMessage]:
        result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == str(session_id))
            .order_by(ChatMessage.created_at)
        )
        return result.scalars().all()
