from __future__ import annotations

from typing import Annotated
from pydantic import BaseModel, Field, StringConstraints

EmailStrAllowLocal = Annotated[
    str,
    StringConstraints(pattern=r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")
]


class RegisterRequest(BaseModel):
    email: EmailStrAllowLocal
    password: str = Field(..., min_length=8)


class AdminRegisterRequest(BaseModel):
    email: EmailStrAllowLocal
    password: str = Field(..., min_length=8)
    invite_code: str = Field(..., min_length=1)


class LoginRequest(BaseModel):
    email: EmailStrAllowLocal
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
