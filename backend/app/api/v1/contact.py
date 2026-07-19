from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.contact import ContactMessage
from app.schemas.contact import ContactMessageIn, ContactMessageOut

router = APIRouter(prefix="/contact", tags=["contact"])

DbSession = Annotated[AsyncSession, Depends(get_db)]

# A person with a genuine question sends one message, maybe two. Anything past
# this in an hour is a script, and the queue is only useful if it isn't drowned.
MAX_PER_EMAIL_PER_HOUR = 5


@router.post("", response_model=ContactMessageOut, status_code=201)
async def submit_message(payload: ContactMessageIn, db: DbSession) -> ContactMessageOut:
    since = datetime.now(UTC) - timedelta(hours=1)

    recent = await db.scalar(
        select(func.count())
        .select_from(ContactMessage)
        .where(
            ContactMessage.email == payload.email,
            ContactMessage.created_at >= since,
        )
    )

    if (recent or 0) >= MAX_PER_EMAIL_PER_HOUR:
        raise HTTPException(
            status_code=429,
            detail=(
                "That's a lot of messages in a short time. Please wait a little "
                "before sending another, or email us directly."
            ),
        )

    message = ContactMessage(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        subject=payload.subject,
        message=payload.message,
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)

    # A reference the sender can quote, without exposing the raw row id.
    return ContactMessageOut(reference=f"MSG{message.created_at:%y%m%d}{message.id:04d}")
