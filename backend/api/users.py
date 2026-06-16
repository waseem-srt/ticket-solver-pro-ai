from __future__ import annotations

from fastapi import APIRouter, Query

from core.dependencies import AdminUser, DB
from schemas.user import UserListOut, UserOut, UserUpdate
from services.user_service import UserService

router = APIRouter(prefix="/admin/users", tags=["Admin - Users"])


@router.get("", response_model=UserListOut)
async def list_users(
    _: AdminUser,
    db: DB,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
):
    svc = UserService(db)
    users, total = await svc.list_users(skip=skip, limit=limit)
    return {"items": users, "total": total}


@router.get("/{user_id}", response_model=UserOut)
async def get_user(_: AdminUser, db: DB, user_id: str):
    svc = UserService(db)
    return await svc.get_user(user_id)


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(_: AdminUser, db: DB, user_id: str, body: UserUpdate):
    svc = UserService(db)
    return await svc.update_user(user_id, role=body.role, is_active=body.is_active)


@router.delete("/{user_id}", status_code=204)
async def deactivate_user(_: AdminUser, db: DB, user_id: str):
    svc = UserService(db)
    await svc.deactivate_user(user_id)
