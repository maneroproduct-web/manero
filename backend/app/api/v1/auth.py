import asyncio
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import CurrentAdmin
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    hash_password,
    needs_rehash,
    verify_password,
)
from app.models.admin import AdminUser

router = APIRouter(prefix="/auth", tags=["auth"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


class LoginIn(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=200)


class LoginOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    admin: "AdminOut"


class AdminOut(BaseModel):
    id: int
    email: str
    name: str


LoginOut.model_rebuild()


@router.post("/login", response_model=LoginOut)
async def login(payload: LoginIn, db: DbSession) -> LoginOut:
    from app.core.config import settings

    admin = await db.scalar(
        select(AdminUser).where(AdminUser.email == payload.email.lower())
    )

    # One message for every failure mode — unknown address, wrong password,
    # deactivated account. Distinguishing them tells an attacker which emails
    # are real staff accounts.
    invalid = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Email or password is incorrect.",
    )

    if admin is None:
        # Hash anyway so a missing account doesn't return noticeably faster than
        # a wrong password, which would leak which addresses exist.
        await asyncio.to_thread(hash_password, payload.password)
        raise invalid

    if not await asyncio.to_thread(
        verify_password, payload.password, admin.password_hash
    ):
        raise invalid

    if not admin.is_active:
        raise invalid

    # Upgrade the stored hash if our parameters have got stronger since signup.
    if needs_rehash(admin.password_hash):
        admin.password_hash = await asyncio.to_thread(hash_password, payload.password)

    admin.last_login_at = datetime.now(UTC)
    await db.commit()

    return LoginOut(
        access_token=create_access_token(str(admin.id), {"email": admin.email}),
        expires_in_minutes=settings.access_token_minutes,
        admin=AdminOut(id=admin.id, email=admin.email, name=admin.name),
    )


@router.get("/me", response_model=AdminOut)
async def me(admin: CurrentAdmin) -> AdminOut:
    """Lets the frontend check whether a stored token is still good."""
    return AdminOut(id=admin.id, email=admin.email, name=admin.name)
