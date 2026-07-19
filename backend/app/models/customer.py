from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Customer(Base):
    """A shopper who has verified a mobile number or email address.

    There is no password. Identity is proven by receiving a one-time code, which
    means there is no password for us to leak and nothing for the customer to
    forget. Either `phone` or `email` is set — whichever they signed in with —
    and the other can be filled in later.
    """

    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Exactly one of these is set at signup. Both are unique where present.
    phone: Mapped[str | None] = mapped_column(
        String(15), unique=True, index=True, nullable=True
    )
    email: Mapped[str | None] = mapped_column(
        String(255), unique=True, index=True, nullable=True
    )

    name: Mapped[str] = mapped_column(String(200), default="")

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    @property
    def identifier(self) -> str:
        return self.phone or self.email or ""

    @property
    def display_name(self) -> str:
        """What the avatar and greeting use."""
        return self.name or self.identifier


class OtpCode(Base):
    """A pending one-time code.

    The code itself is never stored — only a hash, for the same reason passwords
    are hashed: a leaked database should not hand over live login codes.

    Rows are kept after use (marked `consumed`) so a code cannot be replayed,
    and so there is a trail if an account is disputed.
    """

    __tablename__ = "otp_codes"

    id: Mapped[int] = mapped_column(primary_key=True)

    # The phone number or email the code was sent to, normalised.
    destination: Mapped[str] = mapped_column(String(255), index=True)
    channel: Mapped[str] = mapped_column(String(10))  # "sms" | "email"

    code_hash: Mapped[str] = mapped_column(String(255))

    # Wrong guesses. Past the limit the code is dead, so a 6-digit code cannot
    # be brute-forced with a million requests.
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    consumed: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), index=True
    )
