from __future__ import annotations

from fastapi import APIRouter

from core.dependencies import DB
from schemas.auth import (
    AdminRegisterRequest,
    LoginRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
)
from schemas.user import UserOut
from services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=201)
async def register(body: RegisterRequest, db: DB):
    svc = AuthService(db)
    user = await svc.register(email=body.email, password=body.password)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: DB):
    svc = AuthService(db)
    return await svc.login(email=body.email, password=body.password)


@router.post("/admin/register", response_model=UserOut, status_code=201)
async def admin_register(body: AdminRegisterRequest, db: DB):
    """Register a new admin account. Requires a valid invite code."""
    svc = AuthService(db)
    user = await svc.register_admin(
        email=body.email, password=body.password, invite_code=body.invite_code
    )
    return user


@router.post("/admin/login", response_model=TokenResponse)
async def admin_login(body: LoginRequest, db: DB):
    """Login specifically for admin users. Rejects non-admin accounts."""
    svc = AuthService(db)
    return await svc.login_admin(email=body.email, password=body.password)


@router.post("/refresh", response_model=TokenResponse)
async def refresh(body: RefreshRequest, db: DB):
    svc = AuthService(db)
    return await svc.refresh(raw_refresh_token=body.refresh_token)


@router.post("/logout", status_code=204)
async def logout(body: RefreshRequest, db: DB):
    svc = AuthService(db)
    await svc.logout(raw_refresh_token=body.refresh_token)
