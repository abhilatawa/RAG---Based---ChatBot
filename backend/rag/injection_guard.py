# backend/rag/injection_guard.py

import re
from fastapi import HTTPException, status

INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions?",
    r"forget\s+(everything|all|prior)",
    r"pretend\s+(you\s+are|to\s+be)",
    r"you\s+are\s+now\s+a",
    r"act\s+as\s+(?!FinSolve)",
    r"jailbreak",
    r"DAN\s+mode",
    r"developer\s+mode",
    r"system\s+prompt",
    r"<\|.*?\|>",
    r"access_roles?\s*[:=]",
]

COMPILED = [re.compile(p, re.IGNORECASE) for p in INJECTION_PATTERNS]
MAX_LEN  = 1000


class InjectionGuard:
    def validate(self, query: str, user_id: str) -> str:
        if not query or not query.strip():
            raise HTTPException(status_code=400, detail="Query cannot be empty.")
        if len(query) > MAX_LEN:
            raise HTTPException(status_code=400, detail=f"Query too long (max {MAX_LEN} chars).")
        for pattern in COMPILED:
            if pattern.search(query):
                raise HTTPException(status_code=400, detail="Query contains disallowed content.")
        return " ".join(query.split())
