# backend/app/config.py

from __future__ import annotations
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── App ──────────────────────────────────────────────────────
    APP_NAME:    str  = "FinSolve RAG API"
    APP_VERSION: str  = "1.0.0"
    DEBUG:       bool = True
    ENVIRONMENT: str  = "development"

    # ── Security ─────────────────────────────────────────────────
    JWT_SECRET_KEY: str = "finsolve-dev-secret-change-in-production-abc123"
    JWT_ALGORITHM:  str = "HS256"

    # ── Database ─────────────────────────────────────────────────
    DATABASE_URL: str = "sqlite+aiosqlite:///./finsolve.db"

    # ── Redis ────────────────────────────────────────────────────
    REDIS_URL: str  = "redis://localhost:6379/0"
    USE_REDIS: bool = False

    # ── CORS ─────────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = ["http://localhost:8501", "http://127.0.0.1:8501"]

    # ── Qdrant ───────────────────────────────────────────────────
    QDRANT_URL:     str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""

    # ── Ollama ───────────────────────────────────────────────────
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL:    str = "llama3.2"         # chat model
    EMBED_MODEL:     str = "nomic-embed-text" # embedding model

    # ── LLM provider (kept for compatibility) ─────────────────────
    LLM_PROVIDER:    str = "local"
    LLM_MODEL:       str = "llama3.2"
    EMBEDDING_MODEL: str = "nomic-embed-text"
    OPENAI_API_KEY:  str = ""


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
