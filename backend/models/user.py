# backend/models/user.py

from __future__ import annotations
from datetime import datetime
from sqlalchemy import (
    Column, String, Boolean, Integer,
    DateTime, Enum as SAEnum
)
from backend.db.database import Base
from backend.rbac.roles import Role


class User(Base):
    __tablename__ = "users"

    # SQLite-compatible primary key (no gen_random_uuid)
    user_id         = Column(String(36), primary_key=True)
    username        = Column(String(64),  nullable=False, unique=True, index=True)
    email           = Column(String(255), nullable=False, unique=True)
    password_hash   = Column(String,      nullable=False)
    role            = Column(SAEnum(Role, name="user_role"), nullable=False)
    department      = Column(String(64),  nullable=False)
    is_active       = Column(Boolean,     nullable=False, default=True)
    failed_attempts = Column(Integer,     nullable=False, default=0)
    locked_until    = Column(DateTime,    nullable=True)
    last_login      = Column(DateTime,    nullable=True)
    created_at      = Column(DateTime,    nullable=False, default=datetime.utcnow)
    updated_at      = Column(DateTime,    nullable=False, default=datetime.utcnow,
                             onupdate=datetime.utcnow)
