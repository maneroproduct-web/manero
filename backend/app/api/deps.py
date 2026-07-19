"""Shared FastAPI dependencies."""

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import AuthError, decode_access_token
from app.models.admin import AdminUser

# auto_error=False so a missing header produces our own 401 with a useful
# message, rather than FastAPI's bare 403.
bearer = HTTPBearer(auto_error=False)

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def require_admin(
    db: DbSession,
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)] = None,
) -> AdminUser:
    """Gate for every staff-only route.

    Re-reads the user from the database on each request rather than trusting the
    token's contents. That costs one query and means deactivating an account
    takes effect immediately, instead of whenever their token happens to expire.
    """
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not signed in.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if creds is None or not creds.credentials:
        raise unauthorized

    try:
        payload = decode_access_token(creds.credentials)
    except AuthError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    try:
        admin_id = int(payload["sub"])
    except (KeyError, TypeError, ValueError) as exc:
        raise unauthorized from exc

    admin = await db.scalar(select(AdminUser).where(AdminUser.id == admin_id))

    if admin is None or not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="This account is no longer active.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return admin


CurrentAdmin = Annotated[AdminUser, Depends(require_admin)]
