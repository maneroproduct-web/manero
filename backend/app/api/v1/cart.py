from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import get_db
from app.models.cart import Cart, CartItem
from app.models.product import ProductVariant
from app.schemas.cart import CartItemIn, CartItemOut, CartItemQuantityIn, CartOut
from app.services.pricing import compute_totals

router = APIRouter(prefix="/carts", tags=["cart"])

DbSession = Annotated[AsyncSession, Depends(get_db)]


# Serialization walks cart -> items -> variant -> product. Every hop must be
# eager-loaded; a lazy load would raise inside the async session.
CART_LOAD = selectinload(Cart.items).selectinload(CartItem.variant).selectinload(
    ProductVariant.product
)


async def _load_cart(db: AsyncSession, token: str) -> Cart:
    cart = await db.scalar(
        select(Cart)
        .where(Cart.token == token)
        .options(CART_LOAD)
        # populate_existing is required, not incidental. Sessions are created
        # with expire_on_commit=False, so re-selecting a cart already in the
        # identity map hands back its previously loaded `items` collection —
        # stale. After an insert that means responding "cart is empty" to the
        # request that just filled it.
        .execution_options(populate_existing=True)
    )
    if cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")
    return cart


def _serialize(cart: Cart) -> CartOut:
    totals = compute_totals(cart)
    items = [
        CartItemOut(
            id=item.id,
            variant_id=item.variant_id,
            quantity=item.quantity,
            size_grams=item.variant.size_grams,
            sku=item.variant.sku,
            unit_price_paise=item.variant.price_paise,
            line_total_paise=item.variant.price_paise * item.quantity,
            stock_qty=item.variant.stock_qty,
            product_name=item.variant.product.name,
            product_slug=item.variant.product.slug,
            image_url=item.variant.product.image_url,
        )
        for item in cart.items
    ]
    return CartOut(
        token=cart.token,
        items=items,
        item_count=totals.item_count,
        subtotal_paise=totals.subtotal_paise,
        shipping_paise=totals.shipping_paise,
        total_paise=totals.total_paise,
        free_shipping_threshold_paise=settings.free_shipping_threshold_paise,
    )


async def _refresh(db: AsyncSession, cart: Cart) -> Cart:
    """Commit, then re-read through CART_LOAD so the full graph is eager-loaded."""
    await db.commit()
    return await _load_cart(db, cart.token)


@router.post("", response_model=CartOut, status_code=201)
async def create_cart(db: DbSession) -> CartOut:
    cart = Cart()
    db.add(cart)
    await db.commit()
    await db.refresh(cart)
    return _serialize(cart)


@router.get("/{token}", response_model=CartOut)
async def get_cart(token: str, db: DbSession) -> CartOut:
    return _serialize(await _load_cart(db, token))


@router.post("/{token}/items", response_model=CartOut)
async def add_item(token: str, payload: CartItemIn, db: DbSession) -> CartOut:
    cart = await _load_cart(db, token)

    variant = await db.get(ProductVariant, payload.variant_id)
    if variant is None:
        raise HTTPException(status_code=404, detail="Variant not found")

    existing = next((i for i in cart.items if i.variant_id == variant.id), None)
    desired = (existing.quantity if existing else 0) + payload.quantity

    if desired > variant.stock_qty:
        raise HTTPException(
            status_code=409,
            detail=f"Only {variant.stock_qty} left in stock for this size.",
        )

    if existing:
        existing.quantity = desired
    else:
        db.add(CartItem(cart_id=cart.id, variant_id=variant.id, quantity=payload.quantity))

    return _serialize(await _refresh(db, cart))


@router.patch("/{token}/items/{item_id}", response_model=CartOut)
async def update_item(
    token: str, item_id: int, payload: CartItemQuantityIn, db: DbSession
) -> CartOut:
    cart = await _load_cart(db, token)

    item = next((i for i in cart.items if i.id == item_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not in cart")

    if payload.quantity == 0:
        await db.delete(item)
    elif payload.quantity > item.variant.stock_qty:
        raise HTTPException(
            status_code=409,
            detail=f"Only {item.variant.stock_qty} left in stock for this size.",
        )
    else:
        item.quantity = payload.quantity

    return _serialize(await _refresh(db, cart))


@router.delete("/{token}/items/{item_id}", response_model=CartOut)
async def remove_item(token: str, item_id: int, db: DbSession) -> CartOut:
    cart = await _load_cart(db, token)

    item = next((i for i in cart.items if i.id == item_id), None)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not in cart")

    await db.delete(item)
    return _serialize(await _refresh(db, cart))
