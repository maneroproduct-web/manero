"""Single source of truth for cart totals.

Both the cart display and checkout call this. Prices are always read from the
variant rows in the database — the client never supplies a price.
"""

from dataclasses import dataclass

from app.core.config import settings
from app.models.cart import Cart


@dataclass(frozen=True)
class CartTotals:
    subtotal_paise: int
    shipping_paise: int
    total_paise: int
    item_count: int


def shipping_for(subtotal_paise: int) -> int:
    if subtotal_paise <= 0:
        return 0
    if subtotal_paise >= settings.free_shipping_threshold_paise:
        return 0
    return settings.shipping_fee_paise


def compute_totals(cart: Cart) -> CartTotals:
    subtotal = sum(item.variant.price_paise * item.quantity for item in cart.items)
    item_count = sum(item.quantity for item in cart.items)
    shipping = shipping_for(subtotal)
    return CartTotals(
        subtotal_paise=subtotal,
        shipping_paise=shipping,
        total_paise=subtotal + shipping,
        item_count=item_count,
    )
