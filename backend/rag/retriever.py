# backend/rag/retriever.py

from __future__ import annotations
from dataclasses import dataclass
from qdrant_client.models import Filter, FieldCondition, MatchAny
from backend.vector_db.qdrant_client import get_qdrant, COLLECTION_NAME
from backend.rbac.roles import Role


@dataclass
class RetrievedChunk:
    text:        str
    score:       float
    document_id: str
    filename:    str
    page_number: int
    chunk_index: int
    department:  str


class RoleFilteredRetriever:
    """
    Semantic search with mandatory role-based access control.

    SECURITY: The role filter runs inside Qdrant before vector scoring.
    Unauthorized chunks are never returned — not even to be filtered in Python.
    """

    def __init__(self, top_k: int = 5):
        self.top_k = min(top_k, 10)

    async def search(
        self,
        query_vector: list[float],
        role: Role,
        top_k: int | None = None,
    ) -> list[RetrievedChunk]:
        k      = min(top_k or self.top_k, 10)
        qdrant = await get_qdrant()

        # Build role filter — runs server-side in Qdrant
        role_filter = Filter(
            must=[
                FieldCondition(
                    key="access_roles",
                    match=MatchAny(any=[role.value, "all"]),
                )
            ]
        )

        results = await qdrant.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            query_filter=role_filter,
            limit=k,
            with_payload=True,
            score_threshold=0.3,
        )

        chunks = []
        for hit in results:
            if not hit.payload:
                continue
            chunks.append(RetrievedChunk(
                text=        hit.payload.get("text", ""),
                score=       hit.score,
                document_id= hit.payload.get("document_id", ""),
                filename=    hit.payload.get("filename", ""),
                page_number= hit.payload.get("page_number", 1),
                chunk_index= hit.payload.get("chunk_index", 0),
                department=  hit.payload.get("department", ""),
            ))

        return self._deduplicate(chunks)

    @staticmethod
    def _deduplicate(chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
        seen: dict[tuple, RetrievedChunk] = {}
        for chunk in chunks:
            key = (chunk.document_id, chunk.chunk_index)
            if key not in seen or chunk.score > seen[key].score:
                seen[key] = chunk
        return sorted(seen.values(), key=lambda c: c.score, reverse=True)
