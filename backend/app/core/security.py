"""Password hashing and session tokens.

Two rules this module exists to enforce:

  1. Plaintext passwords never leave this file. Everything else deals in hashes.
  2. Token verification fails closed. Any doubt — bad signature, expiry, wrong
     shape — is rejected, never "probably fine".
"""

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from app.core.config import settings

# Argon2id defaults: memory-hard, so a stolen database is expensive to attack
# even with GPUs. Do not lower these to speed up tests.
_hasher = PasswordHasher()

ALGORITHM = "HS256"


class AuthError(Exception):
    """Raised when a token cannot be trusted."""


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """False on any failure — never raises for a wrong password.

    A malformed hash in the database is treated as a failed login rather than a
    500, so a corrupt row cannot be probed for information.
    """
    try:
        return _hasher.verify(password_hash, password)
    except (VerifyMismatchError, InvalidHashError, Exception):
        return False


def needs_rehash(password_hash: str) -> bool:
    """True when the stored hash uses weaker parameters than we now use."""
    try:
        return _hasher.check_needs_rehash(password_hash)
    except Exception:
        return False


def create_access_token(subject: str, extra: dict[str, Any] | None = None) -> str:
    now = datetime.now(UTC)
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_minutes),
        "typ": "admin",
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and validate, or raise AuthError.

    `jwt.decode` verifies the signature and expiry. The explicit `typ` check
    stops a token minted for some other purpose later being replayed here.
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=[ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise AuthError("Your session has expired. Please sign in again.") from exc
    except jwt.InvalidTokenError as exc:
        raise AuthError("Invalid session token.") from exc

    if payload.get("typ") != "admin":
        raise AuthError("Invalid session token.")

    return payload
