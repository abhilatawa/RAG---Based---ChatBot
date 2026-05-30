# backend/rbac/roles.py

from enum import Enum


class Role(str, Enum):
    FINANCE     = "finance"
    HR          = "hr"
    ENGINEERING = "engineering"
    MARKETING   = "marketing"
    C_LEVEL     = "c_level"
    EMPLOYEE    = "employee"
