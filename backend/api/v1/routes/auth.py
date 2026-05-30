# backend/api/v1/routes/auth.py

from __future__ import annotations
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from backend.app.dependencies import DbSession
from backend.auth.jwt_handler import sign_access_token, sign_refresh_token, verify_refresh_token
from backend.auth.password_handler import verify_password
from backend.models.user import User
from backend.models.schemas import LoginRequest, TokenResponse, RefreshRequest

router = APIRouter()

LOCKOUT_THRESHOLD = 5
LOCKOUT_MINUTES   = 5


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, db: DbSession):
    # Generic error — never reveal if username exists
    auth_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid username or password.",
    )

    # Look up user
    result = await db.execute(
        select(User).where(User.username == body.username)
    )
    user: User | None = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise auth_error

    # Check lockout
    if user.locked_until and user.locked_until > datetime.utcnow():
        remaining = int((user.locked_until - datetime.utcnow()).total_seconds())
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Account locked. Try again in {remaining}s.",
        )

    # Verify password
    if not verify_password(body.password, user.password_hash):
        user.failed_attempts += 1
        if user.failed_attempts >= LOCKOUT_THRESHOLD:
            user.locked_until    = datetime.utcnow() + timedelta(minutes=LOCKOUT_MINUTES)
            user.failed_attempts = 0
        await db.commit()
        raise auth_error

    # Success — reset counters
    user.failed_attempts = 0
    user.locked_until    = None
    user.last_login      = datetime.utcnow()
    await db.commit()

    access_token  = sign_access_token(user.user_id, user.username, user.role.value)
    refresh_token = sign_refresh_token(user.user_id, user.role.value)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        role=user.role.value,
        username=user.username,
    )


@router.post("/refresh")
async def refresh(body: RefreshRequest):
    payload       = verify_refresh_token(body.refresh_token)
    access_token  = sign_access_token(
        payload["sub"], payload.get("username", ""), payload["role"]
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/logout")
async def logout():
    # Stateless JWT — client just discards the token.
    # With Redis session store (Phase 5), we'd revoke here.
    return {"message": "Successfully logged out."}
