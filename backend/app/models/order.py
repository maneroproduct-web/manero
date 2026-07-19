from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import OrderStatus


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_number: Mapped[str] = mapped_column(String(20), unique=True, index=True)

    # Phase 2 will add a nullable users FK here; guest orders stay valid.
    email: Mapped[str] = mapped_column(String(255))
    phone: Mapped[str] = mapped_column(String(20))

    # Which cart this order came from, so it can be emptied once payment clears.
    cart_token: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)

    shipping_name: Mapped[str] = mapped_column(String(200))
    shipping_line1: Mapped[str] = mapped_column(String(255))
    shipping_line2: Mapped[str] = mapped_column(String(255), default="")
    shipping_city: Mapped[str] = mapped_column(String(120))
    shipping_state: Mapped[str] = mapped_column(String(120))
    shipping_pincode: Mapped[str] = mapped_column(String(10))

    subtotal_paise: Mapped[int] = mapped_column(Integer)
    shipping_paise: Mapped[int] = mapped_column(Integer)
    total_paise: Mapped[int] = mapped_column(Integer)

    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, native_enum=False, length=20),
        default=OrderStatus.PENDING,
        index=True,
    )

    # Gateway-neutral: "dummy", "razorpay", or whatever comes next.
    payment_provider: Mapped[str] = mapped_column(String(32), default="dummy")
    provider_order_id: Mapped[str | None] = mapped_column(
        String(64), nullable=True, index=True
    )
    provider_payment_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    paid_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="OrderItem.id",
    )


class OrderItem(Base):
    """Product details are denormalised on purpose.

    An order is a historical record: editing or deleting a product later must not
    change what a past order says was bought, or for how much.
    """

    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), index=True
    )
    # Kept for stock reconciliation, but nulled rather than cascading on delete.
    variant_id: Mapped[int | None] = mapped_column(
        ForeignKey("product_variants.id", ondelete="SET NULL"), nullable=True
    )

    product_name: Mapped[str] = mapped_column(String(200))
    product_slug: Mapped[str] = mapped_column(String(120))
    sku: Mapped[str] = mapped_column(String(64))
    size_grams: Mapped[int] = mapped_column(Integer)
    unit_price_paise: Mapped[int] = mapped_column(Integer)
    quantity: Mapped[int] = mapped_column(Integer)
    line_total_paise: Mapped[int] = mapped_column(Integer)

    order: Mapped[Order] = relationship(back_populates="items")
