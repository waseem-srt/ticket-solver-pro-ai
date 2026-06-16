from __future__ import annotations

from datetime import datetime, timezone
from typing import Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import RefreshToken, User


class UserRepository:
    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create(self, email: str, password_hash: str, role: str = "user") -> User:
        user = User(email=email, password_hash=password_hash, role=role)
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user

    async def get_by_id(self, user_id: str) -> User | None:
        result = await self.db.execute(select(User).where(User.id == str(user_id)))
        return result.scalars().first()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def list_users(self, skip: int = 0, limit: int = 50) -> tuple[Sequence[User], int]:
        count_result = await self.db.execute(select(User))
        all_users = count_result.scalars().all()
        total = len(all_users)
        result = await self.db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all(), total

    async def update(self, user_id: str, **kwargs) -> User | None:
        await self.db.execute(
            update(User).where(User.id == str(user_id)).values(**kwargs)
        )
        await self.db.flush()
        return await self.get_by_id(user_id)

    # ── Refresh tokens ────────────────────────────────────────────────────

    async def create_refresh_token(
        self, user_id: str, token_hash: str, expires_at: datetime
    ) -> RefreshToken:
        token = RefreshToken(
            user_id=str(user_id), token_hash=token_hash, expires_at=expires_at
        )
        self.db.add(token)
        await self.db.flush()
        return token

    async def get_refresh_token(self, token_hash: str) -> RefreshToken | None:
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash,
                RefreshToken.is_revoked == False,  # noqa: E712
                RefreshToken.expires_at > datetime.now(timezone.utc),
            )
        )
        return result.scalars().first()

    async def revoke_refresh_token(self, token_hash: str) -> None:
        await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
            .values(is_revoked=True)
        )
        await self.db.flush()

    async def revoke_all_user_tokens(self, user_id: str) -> None:
        await self.db.execute(
            update(RefreshToken)
            .where(RefreshToken.user_id == str(user_id))
            .values(is_revoked=True)
        )
        await self.db.flush()
