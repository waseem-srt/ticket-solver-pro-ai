from __future__ import annotations

from datetime import datetime

from typing import Annotated
from pydantic import BaseModel, Field, StringConstraints

EmailStrAllowLocal = Annotated[
    str,
    StringConstraints(pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
]


class UserBase(BaseModel):
    email: EmailStrAllowLocal


class UserCreate(UserBase):
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    role: str | None = None
    is_active: bool | None = None


class UserOut(UserBase):
    id: str
    role: str
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserListOut(BaseModel):
    items: list[UserOut]
    total: int
