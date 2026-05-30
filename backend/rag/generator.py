# backend/rag/generator.py

from __future__ import annotations
import json
from typing import AsyncGenerator
import httpx
from backend.app.config import get_settings
from backend.rag.retriever import RetrievedChunk
from backend.rbac.roles import Role
from backend.prompts.prompt_builder import build_prompt

settings = get_settings()

OLLAMA_CHAT_URL = f"{settings.OLLAMA_BASE_URL}/api/generate"
OLLAMA_MODEL    = settings.OLLAMA_MODEL


class LLMGenerator:
    """
    Streams responses from Ollama (llama3.2).
    Yields SSE-formatted JSON strings.
    """

    async def stream(
        self,
        query:  str,
        chunks: list[RetrievedChunk],
        role:   Role,
    ) -> AsyncGenerator[str, None]:

        prompt = build_prompt(query, chunks, role)

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                async with client.stream(
                    "POST",
                    OLLAMA_CHAT_URL,
                    json={
                        "model":  OLLAMA_MODEL,
                        "prompt": prompt,
                        "stream": True,
                        "options": {
                            "temperature": 0.1,
                            "num_predict": 1024,
                        },
                    },
                ) as response:
                    response.raise_for_status()

                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                        try:
                            data = json.loads(line)
                        except json.JSONDecodeError:
                            continue

                        token = data.get("response", "")
                        done  = data.get("done", False)

                        if token:
                            yield self._sse({"delta": token, "done": False})

                        if done:
                            sources = self._format_sources(chunks)
                            yield self._sse({"delta": "", "done": True, "sources": sources})
                            return

        except httpx.ConnectError:
            yield self._sse({
                "delta": "⚠️ Cannot connect to Ollama. Run `ollama serve` and try again.",
                "done":  True, "sources": [],
            })
        except Exception as e:
            yield self._sse({
                "delta": f"⚠️ Generation error: {e}",
                "done":  True, "sources": [],
            })

    async def generate(
        self,
        query:  str,
        chunks: list[RetrievedChunk],
        role:   Role,
    ) -> tuple[str, list[dict]]:
        """
        Non-streaming version — returns (full_answer, sources).
        Used by the non-streaming chat endpoint.
        """
        prompt = build_prompt(query, chunks, role)
        full   = ""

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                r = await client.post(
                    OLLAMA_CHAT_URL,
                    json={
                        "model":  OLLAMA_MODEL,
                        "prompt": prompt,
                        "stream": False,
                        "options": {"temperature": 0.1, "num_predict": 1024},
                    },
                )
                r.raise_for_status()
                data = r.json()
                full = data.get("response", "No response generated.")

        except httpx.ConnectError:
            full = "⚠️ Cannot connect to Ollama. Please run `ollama serve` and try again."
        except Exception as e:
            full = f"⚠️ Generation error: {e}"

        return full, self._format_sources(chunks)

    @staticmethod
    def _sse(data: dict) -> str:
        return f"data: {json.dumps(data)}\n\n"

    @staticmethod
    def _format_sources(chunks: list[RetrievedChunk]) -> list[dict]:
        seen    = set()
        sources = []
        for chunk in chunks:
            key = (chunk.document_id, chunk.page_number)
            if key not in seen:
                seen.add(key)
                sources.append({
                    "document_id": chunk.document_id,
                    "filename":    chunk.filename,
                    "page":        chunk.page_number,
                    "department":  chunk.department,
                    "score":       round(chunk.score, 3),
                })
        return sources
