from datetime import datetime

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class AdminUser(Base):
    """A staff account that can manage the catalog.

    Deliberately separate from any future customer account table: staff and
    customers have different lifecycles and blast radius, and merging them is
    how a privilege-escalation bug gets written.

    Only ever holds a hash — see core/security.py. Create accounts with
    `python -m app.cli create_admin`, never by inserting rows by hand.
    """

    __tablename__ = "admin_users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), default="")

    password_hash: Mapped[str] = mapped_column(String(255))

    # Lets you revoke access without deleting the row (and its audit trail).
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
