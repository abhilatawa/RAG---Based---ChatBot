# backend/app/main.py

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.config import get_settings
from backend.api.middleware.auth_middleware import AuthMiddleware
from backend.api.v1.routes import auth, chat, health
from backend.db.database import init_db

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀  FinSolve API starting...")

    await init_db()
    print("✅  Database ready")

    from backend.scripts.seed_users import seed_if_empty
    await seed_if_empty()
    print("✅  Demo users ready")

    try:
        from backend.vector_db.qdrant_client import ensure_collection
        await ensure_collection()
        print("✅  Qdrant ready")
    except Exception as e:
        print(f"⚠️   Qdrant not reachable — start with: docker run -p 6333:6333 qdrant/qdrant")

    yield

    print("👋  FinSolve API shutting down")


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )

    app.add_middleware(AuthMiddleware)

    app.include_router(auth.router,   prefix="/api/v1/auth",   tags=["Auth"])
    app.include_router(chat.router,   prefix="/api/v1/chat",   tags=["Chat"])
    app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])

    @app.get("/")
    async def root():
        return {"app": settings.APP_NAME, "version": settings.APP_VERSION, "docs": "/docs"}

    return app


app = create_app()
