# backend/api/middleware/auth_middleware.py

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from backend.auth.jwt_handler import verify_access_token
from backend.rbac.roles import Role

PUBLIC_PATHS = {
    "/api/v1/auth/login",
    "/api/v1/auth/refresh",
    "/api/v1/health/live",
    "/api/v1/health/ready",
    "/docs",
    "/openapi.json",
    "/redoc",
}


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing Bearer token.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        token = auth_header.split(" ", 1)[1].strip()
        payload = verify_access_token(token)

        request.state.user_id  = payload["sub"]
        request.state.username = payload["username"]
        request.state.role     = Role(payload["role"])

        return await call_next(request)
