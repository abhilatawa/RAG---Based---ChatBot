# backend/scripts/seed_users.py

from __future__ import annotations
import uuid
from backend.db.database import AsyncSessionLocal
from backend.models.user import User
from backend.auth.password_handler import hash_password
from backend.rbac.roles import Role
from sqlalchemy import select

DEMO_PASSWORD = "Password123!"

DEMO_USERS = [
    {
        "username":   "alice.finance",
        "email":      "alice@finsolve.com",
        "role":       Role.FINANCE,
        "department": "finance",
    },
    {
        "username":   "bob.hr",
        "email":      "bob@finsolve.com",
        "role":       Role.HR,
        "department": "hr",
    },
    {
        "username":   "carol.eng",
        "email":      "carol@finsolve.com",
        "role":       Role.ENGINEERING,
        "department": "engineering",
    },
    {
        "username":   "david.mktg",
        "email":      "david@finsolve.com",
        "role":       Role.MARKETING,
        "department": "marketing",
    },
    {
        "username":   "eve.ceo",
        "email":      "eve@finsolve.com",
        "role":       Role.C_LEVEL,
        "department": "executive",
    },
    {
        "username":   "frank.emp",
        "email":      "frank@finsolve.com",
        "role":       Role.EMPLOYEE,
        "department": "general",
    },
]


async def seed_if_empty() -> None:
    """
    Insert demo users only if the users table is empty.
    Safe to call on every startup — idempotent.
    """
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).limit(1))
        if result.scalar_one_or_none() is not None:
            print("ℹ️   Users already seeded — skipping")
            return

        password_hash = hash_password(DEMO_PASSWORD)

        for data in DEMO_USERS:
            user = User(
                user_id=       str(uuid.uuid4()),
                username=      data["username"],
                email=         data["email"],
                password_hash= password_hash,
                role=          data["role"],
                department=    data["department"],
            )
            session.add(user)

        await session.commit()
        print(f"✅  Seeded {len(DEMO_USERS)} demo users (password: {DEMO_PASSWORD})")
