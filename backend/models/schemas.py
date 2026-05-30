# backend/models/schemas.py

from __future__ import annotations
from typing import Optional
from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=1, max_length=128)


class TokenResponse(BaseModel):
    access_token:  str
    refresh_token: str
    token_type:    str = "bearer"
    role:          str
    username:      str


class RefreshRequest(BaseModel):
    refresh_token: str


class ChatRequest(BaseModel):
    query:      str = Field(..., min_length=1, max_length=1000)
    session_id: Optional[str] = None
    top_k:      int = Field(default=5, ge=1, le=10)


class UserOut(BaseModel):
    user_id:    str
    username:   str
    email:      str
    role:       str
    department: str
    is_active:  bool
    last_login: Optional[str] = None
