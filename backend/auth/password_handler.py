# backend/auth/password_handler.py

import bcrypt

BCRYPT_ROUNDS = 12


def hash_password(plain: str) -> str:
    """Hash a plaintext password with bcrypt."""
    # Truncate to 72 bytes — bcrypt hard limit
    password_bytes = plain.encode("utf-8")[:72]
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    """Constant-time password verification."""
    try:
        password_bytes = plain.encode("utf-8")[:72]
        hashed_bytes   = hashed.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception:
        return False