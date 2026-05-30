# backend/vector_db/qdrant_client.py

from __future__ import annotations
from qdrant_client import AsyncQdrantClient
from qdrant_client.models import (
    VectorParams, Distance, PayloadSchemaType,
    HnswConfigDiff
)
from backend.app.config import get_settings

settings = get_settings()

COLLECTION_NAME = "finsolve_documents"
VECTOR_SIZE     = 768   # nomic-embed-text output dimension

_client: AsyncQdrantClient | None = None


async def get_qdrant() -> AsyncQdrantClient:
    global _client
    if _client is None:
        _client = AsyncQdrantClient(
            url=settings.QDRANT_URL,
            api_key=settings.QDRANT_API_KEY or None,
        )
    return _client


async def ensure_collection() -> None:
    """Create the Qdrant collection if it doesn't exist yet."""
    client = await get_qdrant()

    existing = await client.get_collections()
    names = [c.name for c in existing.collections]

    if COLLECTION_NAME in names:
        print(f"ℹ️   Qdrant collection '{COLLECTION_NAME}' already exists")
        return

    await client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(
            size=VECTOR_SIZE,
            distance=Distance.COSINE,
        ),
        hnsw_config=HnswConfigDiff(m=16, ef_construct=100),
    )

    # Index the access_roles and department fields for fast filtering
    await client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="access_roles",
        field_schema=PayloadSchemaType.KEYWORD,
    )
    await client.create_payload_index(
        collection_name=COLLECTION_NAME,
        field_name="department",
        field_schema=PayloadSchemaType.KEYWORD,
    )

    print(f"✅  Qdrant collection '{COLLECTION_NAME}' created")
