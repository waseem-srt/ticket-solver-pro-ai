from __future__ import annotations

import hashlib
from datetime import timezone

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from core.security import (
    create_access_token,
    create_refresh_token,
    get_token_expiry_dt,
    hash_password,
    verify_password,
)
from models.user import User
from repositories.user_repo import UserRepository
from schemas.auth import TokenResponse


def _hash_token(raw: str) -> str:
    """SHA-256 hash of a raw refresh token for storage."""
    return hashlib.sha256(raw.encode()).hexdigest()


class AuthService:
    def __init__(self, db: AsyncSession) -> None:
        self.repo = UserRepository(db)

    async def register(self, email: str, password: str, role: str = "user") -> User:
        existing = await self.repo.get_by_email(email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        user = await self.repo.create(
            email=email,
            password_hash=hash_password(password),
            role=role,
        )
        return user

    async def register_admin(self, email: str, password: str, invite_code: str) -> User:
        """Register an admin user. Requires valid invite code."""
        if invite_code != settings.admin_invite_code:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Invalid admin invite code",
            )
        existing = await self.repo.get_by_email(email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        user = await self.repo.create(
            email=email,
            password_hash=hash_password(password),
            role="admin",
        )
        return user

    async def login(self, email: str, password: str) -> TokenResponse:
        user = await self.repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated",
            )
        return await self._issue_tokens(user)

    async def login_admin(self, email: str, password: str) -> TokenResponse:
        """Login specifically for admin users. Rejects non-admin users."""
        user = await self.repo.get_by_email(email)
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated",
            )
        if user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This account does not have admin privileges",
            )
        return await self._issue_tokens(user)

    async def refresh(self, raw_refresh_token: str) -> TokenResponse:
        token_hash = _hash_token(raw_refresh_token)
        db_token = await self.repo.get_refresh_token(token_hash)
        if not db_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired refresh token",
            )
        # Rotate: revoke old, issue new pair
        await self.repo.revoke_refresh_token(token_hash)
        user = await self.repo.get_by_id(db_token.user_id)
        if not user or not user.is_active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return await self._issue_tokens(user)

    async def logout(self, raw_refresh_token: str) -> None:
        token_hash = _hash_token(raw_refresh_token)
        await self.repo.revoke_refresh_token(token_hash)

    # ── Private helpers ───────────────────────────────────────────────────

    async def _issue_tokens(self, user: User) -> TokenResponse:
        payload = {"sub": str(user.id), "email": user.email, "role": user.role}
        access_token = create_access_token(payload)
        raw_refresh = create_refresh_token(payload)

        expires_at = get_token_expiry_dt(days=settings.jwt_refresh_token_expire_days)
        await self.repo.create_refresh_token(
            user_id=str(user.id),
            token_hash=_hash_token(raw_refresh),
            expires_at=expires_at,
        )
        return TokenResponse(access_token=access_token, refresh_token=raw_refresh)
