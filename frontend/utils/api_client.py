from __future__ import annotations
import json
from typing import AsyncGenerator, Any
import httpx
import streamlit as st

BASE_URL = "http://localhost:8000/api/v1"
TIMEOUT  = httpx.Timeout(30.0, connect=5.0)


def _headers() -> dict:
    token = st.session_state.get("access_token")
    return {"Authorization": f"Bearer {token}"} if token else {}


class APIClient:

    @staticmethod
    async def login(username: str, password: str) -> dict:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            r = await client.post(
                f"{BASE_URL}/auth/login",
                json={"username": username, "password": password},
            )
            r.raise_for_status()
            return r.json()

    @staticmethod
    async def logout(refresh_token: str) -> None:
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT) as client:
                await client.post(
                    f"{BASE_URL}/auth/logout",
                    json={"refresh_token": refresh_token},
                    headers=_headers(),
                )
        except Exception:
            pass  # Best-effort logout

    @staticmethod
    async def stream_query(
        query: str, session_id: str, top_k: int = 5
    ) -> AsyncGenerator[dict, None]:
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            async with client.stream(
                "POST",
                f"{BASE_URL}/chat/query",
                json={"query": query, "session_id": session_id, "top_k": top_k},
                headers={**_headers(), "Accept": "text/event-stream"},
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        try:
                            yield json.loads(line[6:])
                        except json.JSONDecodeError:
                            continue
