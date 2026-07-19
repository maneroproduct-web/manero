from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ContactMessage(Base):
    """An enquiry sent from the Contact page.

    Stored rather than emailed: the project has no mail provider wired up, and a
    form that quietly discards what someone typed is worse than no form at all.
    Read them with `./db.sh "SELECT * FROM contact_messages WHERE NOT handled"`.
    """

    __tablename__ = "contact_messages"

    id: Mapped[int] = mapped_column(primary_key=True)

    name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(255), index=True)
    phone: Mapped[str] = mapped_column(String(20), default="")
    subject: Mapped[str] = mapped_column(String(120), default="general")
    message: Mapped[str] = mapped_column(Text)

    # Flip to true once someone has replied, so the unhandled queue stays useful.
    handled: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
