# backend/ingestion/ingest.py

from __future__ import annotations
import asyncio
import uuid
import sys
import os
from pathlib import Path

# Add project root to path when run as a script
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from qdrant_client.models import PointStruct
from backend.rag.embedder           import EmbeddingService
from backend.vector_db.qdrant_client import get_qdrant, ensure_collection, COLLECTION_NAME

# Maps directory name → (department, access_roles)
DEPT_POLICY = {
    "finance":     ("finance",     ["finance",     "c_level"]),
    "hr":          ("hr",          ["hr",           "c_level"]),
    "engineering": ("engineering", ["engineering", "c_level"]),
    "marketing":   ("marketing",   ["marketing",   "c_level"]),
    "general":     ("general",     ["all"]),          # "all" = every role
    "executive":   ("executive",   ["c_level"]),
}

CHUNK_SIZE    = 1500   # characters per chunk
CHUNK_OVERLAP = 150    # character overlap between chunks


def chunk_text(text: str, size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Split text into overlapping character-level chunks."""
    chunks = []
    start  = 0
    while start < len(text):
        end = start + size
        chunks.append(text[start:end].strip())
        start = end - overlap
    return [c for c in chunks if len(c) > 50]   # Drop tiny trailing chunks


async def ingest_file(file_path: Path, embedder: EmbeddingService) -> dict:
    """Ingest a single .txt file into Qdrant."""
    qdrant = await get_qdrant()

    # Determine department from parent folder name
    parent      = file_path.parent.name.lower()
    department, access_roles = DEPT_POLICY.get(parent, ("general", ["all"]))

    # Read text
    text = file_path.read_text(encoding="utf-8")

    # Chunk it
    chunks = chunk_text(text)

    # Embed all chunks
    vectors = await embedder.embed_batch(chunks)

    # Build Qdrant points
    document_id = str(uuid.uuid4())
    points = []
    for i, (chunk_text_str, vector) in enumerate(zip(chunks, vectors)):
        points.append(PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={
                "access_roles": access_roles,
                "department":   department,
                "document_id":  document_id,
                "filename":     file_path.name,
                "page_number":  i + 1,          # treat chunk index as page
                "chunk_index":  i,
                "total_chunks": len(chunks),
                "text":         chunk_text_str,
                "char_count":   len(chunk_text_str),
            }
        ))

    # Upsert to Qdrant in one batch
    await qdrant.upsert(collection_name=COLLECTION_NAME, points=points)

    return {
        "filename":     file_path.name,
        "department":   department,
        "access_roles": access_roles,
        "chunks":       len(points),
    }


async def ingest_directory(docs_dir: Path) -> None:
    """Ingest all .txt files found under docs_dir recursively."""
    await ensure_collection()

    embedder = EmbeddingService()
    files    = list(docs_dir.rglob("*.txt")) + list(docs_dir.rglob("*.pdf"))

    if not files:
        print(f"No .txt or .pdf files found in {docs_dir}")
        return

    print(f"Found {len(files)} files — starting ingestion...\n")

    for i, file_path in enumerate(files, 1):
        try:
            result = await ingest_file(file_path, embedder)
            print(
                f"[{i}/{len(files)}] ✅ {result['filename']}"
                f" → {result['chunks']} chunks"
                f" | dept: {result['department']}"
                f" | roles: {result['access_roles']}"
            )
        except Exception as e:
            print(f"[{i}/{len(files)}] ❌ {file_path.name}: {e}")

    print(f"\n🎉 Ingestion complete!")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="FinSolve document ingestion")
    parser.add_argument(
        "--dir",
        type=Path,
        default=Path("sample_docs"),
        help="Directory containing documents to ingest",
    )
    args = parser.parse_args()
    asyncio.run(ingest_directory(args.dir))
