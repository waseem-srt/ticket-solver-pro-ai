from __future__ import annotations

from typing import Sequence

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from repositories.user_repo import UserRepository


class UserService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = UserRepository(db)

    async def list_users(self, skip: int = 0, limit: int = 50) -> tuple[Sequence[User], int]:
        return await self.repo.list_users(skip=skip, limit=limit)

    async def get_user(self, user_id: str) -> User:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    async def update_user(self, user_id: str, role: str | None, is_active: bool | None) -> User:
        updates: dict = {}
        if role is not None:
            if role not in ("admin", "user"):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="Role must be 'admin' or 'user'",
                )
            updates["role"] = role
        if is_active is not None:
            updates["is_active"] = is_active
        user = await self.repo.update(user_id, **updates)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user

    async def deactivate_user(self, user_id: str) -> None:
        user = await self.repo.get_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        await self.repo.update(user_id, is_active=False)
