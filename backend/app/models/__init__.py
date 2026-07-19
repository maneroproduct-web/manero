"""Importing every model here ensures Alembic's autogenerate sees them all."""

from app.models.admin import AdminUser
from app.models.cart import Cart, CartItem
from app.models.contact import ContactMessage
from app.models.enums import BeanType, Flavour, Grind, OrderStatus, RoastLevel
from app.models.order import Order, OrderItem
from app.models.product import Product, ProductVariant

__all__ = [
    "AdminUser",
    "BeanType",
    "Cart",
    "CartItem",
    "ContactMessage",
    "Flavour",
    "Grind",
    "Order",
    "OrderItem",
    "OrderStatus",
    "Product",
    "ProductVariant",
    "RoastLevel",
]
