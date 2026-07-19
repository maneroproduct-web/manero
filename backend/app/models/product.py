from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.enums import BeanType, Flavour, Grind, RoastLevel


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    slug: Mapped[str] = mapped_column(String(120), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")

    bean_type: Mapped[BeanType] = mapped_column(
        Enum(BeanType, native_enum=False, length=20), index=True
    )
    roast_level: Mapped[RoastLevel] = mapped_column(
        Enum(RoastLevel, native_enum=False, length=20), index=True
    )
    grind: Mapped[Grind] = mapped_column(
        Enum(Grind, native_enum=False, length=20), index=True
    )
    flavour: Mapped[Flavour] = mapped_column(
        Enum(Flavour, native_enum=False, length=20), index=True
    )

    origin: Mapped[str] = mapped_column(String(120), default="")
    tasting_notes: Mapped[str] = mapped_column(String(300), default="")
    image_url: Mapped[str] = mapped_column(String(500), default="")

    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    is_bestseller: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    variants: Mapped[list["ProductVariant"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductVariant.size_grams",
        lazy="selectin",
    )


class ProductVariant(Base):
    __tablename__ = "product_variants"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("products.id", ondelete="CASCADE"), index=True
    )

    sku: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    size_grams: Mapped[int] = mapped_column(Integer)

    # All money is integer paise. Never float.
    price_paise: Mapped[int] = mapped_column(Integer)
    # Struck-through "was" price; null when not on offer.
    compare_at_price_paise: Mapped[int | None] = mapped_column(Integer, nullable=True)

    stock_qty: Mapped[int] = mapped_column(Integer, default=0)

    product: Mapped[Product] = relationship(back_populates="variants")

    @property
    def in_stock(self) -> bool:
        return self.stock_qty > 0
