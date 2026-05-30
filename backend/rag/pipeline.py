# backend/rag/pipeline.py

from __future__ import annotations
from typing import AsyncGenerator

from backend.rag.injection_guard import InjectionGuard
from backend.rag.embedder        import EmbeddingService
from backend.rag.retriever       import RoleFilteredRetriever
from backend.rag.generator       import LLMGenerator
from backend.rbac.roles          import Role


class RAGPipeline:
    """
    Orchestrates the full RAG flow:
    sanitize → embed → retrieve (role-filtered) → generate
    """

    def __init__(self, top_k: int = 5):
        self.guard     = InjectionGuard()
        self.embedder  = EmbeddingService()
        self.retriever = RoleFilteredRetriever(top_k=top_k)
        self.generator = LLMGenerator()

    async def run(
        self,
        query:   str,
        role:    Role,
        user_id: str,
    ) -> AsyncGenerator[str, None]:
        """Streaming pipeline — yields SSE JSON strings."""
        clean_query  = self.guard.validate(query, user_id)
        query_vector = await self.embedder.embed_query(clean_query)
        chunks       = await self.retriever.search(query_vector, role)

        async for sse in self.generator.stream(clean_query, chunks, role):
            yield sse

    async def run_sync(
        self,
        query:   str,
        role:    Role,
        user_id: str,
    ) -> tuple[str, list[dict]]:
        """Non-streaming pipeline — returns (answer, sources)."""
        clean_query  = self.guard.validate(query, user_id)
        query_vector = await self.embedder.embed_query(clean_query)
        chunks       = await self.retriever.search(query_vector, role)
        answer, sources = await self.generator.generate(clean_query, chunks, role)
        return answer, sources
