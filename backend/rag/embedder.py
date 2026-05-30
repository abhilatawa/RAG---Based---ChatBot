# backend/rag/embedder.py

from __future__ import annotations
import asyncio
import httpx
from backend.app.config import get_settings

settings = get_settings()

OLLAMA_EMBED_URL = f"{settings.OLLAMA_BASE_URL}/api/embeddings"
EMBED_MODEL      = "nomic-embed-text"
MAX_RETRIES      = 3
RETRY_DELAY      = 1.0   # seconds


class EmbeddingService:
    """
    Generates text embeddings using Ollama's nomic-embed-text model.
    Output dimension: 768
    """

    def __init__(self):
        self.model      = EMBED_MODEL
        self.dimensions = 768

    async def embed_query(self, text: str) -> list[float]:
        """Embed a single query string."""
        return await self._embed(text)

    async def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed multiple texts concurrently (max 10 at a time)."""
        semaphore = asyncio.Semaphore(10)

        async def bounded_embed(text: str) -> list[float]:
            async with semaphore:
                return await self._embed(text)

        return await asyncio.gather(*[bounded_embed(t) for t in texts])

    async def _embed(self, text: str) -> list[float]:
        """Single text embedding with retry."""
        text = text.strip()
        if not text:
            return [0.0] * self.dimensions

        for attempt in range(MAX_RETRIES):
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    r = await client.post(
                        OLLAMA_EMBED_URL,
                        json={"model": self.model, "prompt": text},
                    )
                    r.raise_for_status()
                    data = r.json()
                    return data["embedding"]

            except httpx.ConnectError:
                raise RuntimeError(
                    "Cannot connect to Ollama. "
                    "Make sure Ollama is running: `ollama serve`"
                )
            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    raise RuntimeError(f"Embedding failed: {e}") from e
                await asyncio.sleep(RETRY_DELAY * (2 ** attempt))

        return [0.0] * self.dimensions
