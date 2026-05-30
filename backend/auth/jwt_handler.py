# backend/auth/jwt_handler.py

from __future__ import annotations
import time
from typing import Any
from jose import jwt, JWTError, ExpiredSignatureError
from fastapi import HTTPException, status
from backend.app.config import get_settings

settings = get_settings()

ACCESS_EXPIRY  = 15 * 60          # 15 minutes
REFRESH_EXPIRY = 7 * 24 * 60 * 60 # 7 days


def sign_access_token(user_id: str, username: str, role: str) -> str:
    now = int(time.time())
    payload = {
        "sub":      user_id,
        "username": username,
        "role":     role,
        "iat":      now,
        "exp":      now + ACCESS_EXPIRY,
        "type":     "access",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def sign_refresh_token(user_id: str, role: str) -> str:
    now = int(time.time())
    payload = {
        "sub":  user_id,
        "role": role,
        "iat":  now,
        "exp":  now + REFRESH_EXPIRY,
        "type": "refresh",
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def verify_refresh_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM],
        )
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type.",
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        )
