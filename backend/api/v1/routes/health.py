# backend/api/v1/routes/health.py

from fastapi import APIRouter
from backend.db.database import engine
import sqlalchemy

router = APIRouter()


@router.get("/live")
async def liveness():
    return {"status": "ok"}


@router.get("/ready")
async def readiness():
    db_ok = False
    try:
        async with engine.connect() as conn:
            await conn.execute(sqlalchemy.text("SELECT 1"))
        db_ok = True
    except Exception:
        pass

    return {
        "status":   "ok" if db_ok else "degraded",
        "database": db_ok,
    }
