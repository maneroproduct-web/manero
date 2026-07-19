"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-19

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "products",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("slug", sa.String(length=120), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "bean_type",
            sa.Enum("ARABICA", "ROBUSTA", "BLEND", name="beantype", native_enum=False, length=20),
            nullable=False,
        ),
        sa.Column(
            "roast_level",
            sa.Enum("LIGHT", "MEDIUM", "DARK", name="roastlevel", native_enum=False, length=20),
            nullable=False,
        ),
        sa.Column(
            "grind",
            sa.Enum(
                "WHOLE_BEAN", "FILTER", "ESPRESSO", "INSTANT",
                name="grind", native_enum=False, length=20,
            ),
            nullable=False,
        ),
        sa.Column(
            "flavour",
            sa.Enum(
                "ORIGINAL", "HAZELNUT", "VANILLA", "CARAMEL", "MOCHA",
                name="flavour", native_enum=False, length=20,
            ),
            nullable=False,
        ),
        sa.Column("origin", sa.String(length=120), nullable=False),
        sa.Column("tasting_notes", sa.String(length=300), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_bestseller", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_products_slug"), "products", ["slug"], unique=True)
    op.create_index(op.f("ix_products_bean_type"), "products", ["bean_type"])
    op.create_index(op.f("ix_products_roast_level"), "products", ["roast_level"])
    op.create_index(op.f("ix_products_grind"), "products", ["grind"])
    op.create_index(op.f("ix_products_flavour"), "products", ["flavour"])
    op.create_index(op.f("ix_products_is_active"), "products", ["is_active"])
    op.create_index(op.f("ix_products_is_bestseller"), "products", ["is_bestseller"])

    op.create_table(
        "product_variants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("sku", sa.String(length=64), nullable=False),
        sa.Column("size_grams", sa.Integer(), nullable=False),
        sa.Column("price_paise", sa.Integer(), nullable=False),
        sa.Column("compare_at_price_paise", sa.Integer(), nullable=True),
        sa.Column("stock_qty", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_product_variants_product_id"), "product_variants", ["product_id"])
    op.create_index(op.f("ix_product_variants_sku"), "product_variants", ["sku"], unique=True)

    op.create_table(
        "carts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("token", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_carts_token"), "carts", ["token"], unique=True)

    op.create_table(
        "cart_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cart_id", sa.Integer(), nullable=False),
        sa.Column("variant_id", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["cart_id"], ["carts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["variant_id"], ["product_variants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cart_id", "variant_id", name="uq_cart_variant"),
    )
    op.create_index(op.f("ix_cart_items_cart_id"), "cart_items", ["cart_id"])
    op.create_index(op.f("ix_cart_items_variant_id"), "cart_items", ["variant_id"])

    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_number", sa.String(length=20), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=20), nullable=False),
        sa.Column("cart_token", sa.String(length=32), nullable=True),
        sa.Column("shipping_name", sa.String(length=200), nullable=False),
        sa.Column("shipping_line1", sa.String(length=255), nullable=False),
        sa.Column("shipping_line2", sa.String(length=255), nullable=False),
        sa.Column("shipping_city", sa.String(length=120), nullable=False),
        sa.Column("shipping_state", sa.String(length=120), nullable=False),
        sa.Column("shipping_pincode", sa.String(length=10), nullable=False),
        sa.Column("subtotal_paise", sa.Integer(), nullable=False),
        sa.Column("shipping_paise", sa.Integer(), nullable=False),
        sa.Column("total_paise", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("PENDING", "PAID", "FAILED", name="orderstatus", native_enum=False, length=20),
            nullable=False,
        ),
        sa.Column("payment_provider", sa.String(length=32), nullable=False),
        sa.Column("provider_order_id", sa.String(length=64), nullable=True),
        sa.Column("provider_payment_id", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_orders_order_number"), "orders", ["order_number"], unique=True)
    op.create_index(op.f("ix_orders_status"), "orders", ["status"])
    op.create_index(op.f("ix_orders_provider_order_id"), "orders", ["provider_order_id"])
    op.create_index(op.f("ix_orders_cart_token"), "orders", ["cart_token"])

    op.create_table(
        "order_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("variant_id", sa.Integer(), nullable=True),
        sa.Column("product_name", sa.String(length=200), nullable=False),
        sa.Column("product_slug", sa.String(length=120), nullable=False),
        sa.Column("sku", sa.String(length=64), nullable=False),
        sa.Column("size_grams", sa.Integer(), nullable=False),
        sa.Column("unit_price_paise", sa.Integer(), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("line_total_paise", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["variant_id"], ["product_variants.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_order_items_order_id"), "order_items", ["order_id"])


def downgrade() -> None:
    op.drop_table("order_items")
    op.drop_table("orders")
    op.drop_table("cart_items")
    op.drop_table("carts")
    op.drop_table("product_variants")
    op.drop_table("products")
