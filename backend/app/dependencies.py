# backend/app/dependencies.py

from __future__ import annotations
from typing import Annotated
from fastapi import Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.database import get_db
from backend.rbac.roles import Role


class CurrentUser:
    __slots__ = ("user_id", "username", "role")

    def __init__(self, user_id: str, username: str, role: Role):
        self.user_id  = user_id
        self.username = username
        self.role     = role


def get_current_user(request: Request) -> CurrentUser:
    user_id  = getattr(request.state, "user_id",  None)
    username = getattr(request.state, "username", None)
    role     = getattr(request.state, "role",     None)

    if not all([user_id, username, role]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated.",
        )
    return CurrentUser(user_id=user_id, username=username, role=role)


DbSession = Annotated[AsyncSession, Depends(get_db)]
AuthUser  = Annotated[CurrentUser,  Depends(get_current_user)]
