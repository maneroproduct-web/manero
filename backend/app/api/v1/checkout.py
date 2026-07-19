import logging
import secrets
from datetime import UTC, datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.models.cart import Cart, CartItem
from app.models.enums import OrderStatus
from app.models.order import Order, OrderItem
from app.models.product import ProductVariant
from app.schemas.checkout import (
    CreateOrderIn,
    CreateOrderOut,
    DummyPayIn,
    DummyPayOut,
    OrderItemOut,
    OrderOut,
    VerifyPaymentIn,
)
from app.services.payments import DummyProvider, PaymentError, get_provider
from app.services.pricing import compute_totals

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/checkout", tags=["checkout"])

DbSession = Annotated[AsyncSession, Depends(get_db)]

CART_LOAD = selectinload(Cart.items).selectinload(CartItem.variant).selectinload(
    ProductVariant.product
)


def _new_order_number() -> str:
    stamp = datetime.now(UTC).strftime("%y%m%d")
    return f"MNR{stamp}{secrets.randbelow(10_000):04d}"


def _serialize_order(order: Order) -> OrderOut:
    return OrderOut(
        order_number=order.order_number,
        status=order.status,
        email=order.email,
        subtotal_paise=order.subtotal_paise,
        shipping_paise=order.shipping_paise,
        total_paise=order.total_paise,
        shipping_name=order.shipping_name,
        shipping_line1=order.shipping_line1,
        shipping_line2=order.shipping_line2,
        shipping_city=order.shipping_city,
        shipping_state=order.shipping_state,
        shipping_pincode=order.shipping_pincode,
        items=[
            OrderItemOut(
                product_name=i.product_name,
                product_slug=i.product_slug,
                size_grams=i.size_grams,
                quantity=i.quantity,
                unit_price_paise=i.unit_price_paise,
                line_total_paise=i.line_total_paise,
            )
            for i in order.items
        ],
    )


@router.post("/create-order", response_model=CreateOrderOut)
async def create_order(payload: CreateOrderIn, db: DbSession) -> CreateOrderOut:
    cart = await db.scalar(
        select(Cart).where(Cart.token == payload.cart_token).options(CART_LOAD)
    )
    if cart is None:
        raise HTTPException(status_code=404, detail="Cart not found")
    if not cart.items:
        raise HTTPException(status_code=400, detail="Your cart is empty")

    # Re-check stock before taking money. Between add-to-cart and checkout,
    # someone else may have bought the last bag.
    #
    # The rows are locked FOR UPDATE so two checkouts racing for the same last
    # bag are serialised: the second waits, then sees the first one's effect
    # instead of reading the same pre-decrement value and both passing.
    # (SQLite ignores FOR UPDATE, so the test suite is unaffected.)
    variant_ids = [item.variant_id for item in cart.items]
    locked = (
        await db.scalars(
            select(ProductVariant)
            .where(ProductVariant.id.in_(variant_ids))
            .with_for_update()
        )
    ).all()
    stock_by_id = {v.id: v.stock_qty for v in locked}

    for item in cart.items:
        available = stock_by_id.get(item.variant_id, 0)
        if item.quantity > available:
            raise HTTPException(
                status_code=409,
                detail=(
                    f"{item.variant.product.name} ({item.variant.size_grams}g) "
                    f"only has {available} left."
                ),
            )

    try:
        provider = get_provider()
    except PaymentError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    # Totals are recomputed from the database. Nothing the client sent is trusted.
    totals = compute_totals(cart)

    order = Order(
        order_number=_new_order_number(),
        email=payload.email,
        phone=payload.phone,
        cart_token=cart.token,
        shipping_name=payload.shipping.name,
        shipping_line1=payload.shipping.line1,
        shipping_line2=payload.shipping.line2,
        shipping_city=payload.shipping.city,
        shipping_state=payload.shipping.state,
        shipping_pincode=payload.shipping.pincode,
        subtotal_paise=totals.subtotal_paise,
        shipping_paise=totals.shipping_paise,
        total_paise=totals.total_paise,
        status=OrderStatus.PENDING,
        payment_provider=provider.name,
    )
    db.add(order)
    await db.flush()

    for item in cart.items:
        db.add(
            OrderItem(
                order_id=order.id,
                variant_id=item.variant_id,
                product_name=item.variant.product.name,
                product_slug=item.variant.product.slug,
                sku=item.variant.sku,
                size_grams=item.variant.size_grams,
                unit_price_paise=item.variant.price_paise,
                quantity=item.quantity,
                line_total_paise=item.variant.price_paise * item.quantity,
            )
        )

    try:
        order.provider_order_id = provider.create_order(
            amount_paise=totals.total_paise, receipt=order.order_number
        )
    except PaymentError as exc:
        await db.rollback()
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    await db.commit()

    return CreateOrderOut(
        order_number=order.order_number,
        provider=provider.name,
        provider_order_id=order.provider_order_id,
        public_key=provider.public_key(),
        amount_paise=order.total_paise,
    )


@router.post("/dummy-pay", response_model=DummyPayOut)
async def dummy_pay(payload: DummyPayIn, db: DbSession) -> DummyPayOut:
    """Stand in for the gateway's payment UI while PAYMENT_PROVIDER=dummy.

    Returns a callback payload shaped exactly like a real gateway's, so the
    frontend then calls /verify along the normal path. Signing happens here so
    the signing secret never reaches the browser.

    Refuses to run unless the dummy provider is actually the active one.
    """
    provider = get_provider()
    if not isinstance(provider, DummyProvider):
        raise HTTPException(
            status_code=404,
            detail="Dummy payments are not enabled.",
        )

    order = await db.scalar(
        select(Order).where(Order.provider_order_id == payload.provider_order_id)
    )
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    payment_id = f"dummy_pay_{secrets.token_hex(8)}"

    if not payload.succeed:
        # Deliberately wrong signature, so /verify rejects it exactly as it
        # would a genuinely failed or forged payment.
        return DummyPayOut(
            provider_order_id=payload.provider_order_id,
            provider_payment_id=payment_id,
            signature="invalid-signature-simulated-failure",
        )

    return DummyPayOut(
        provider_order_id=payload.provider_order_id,
        provider_payment_id=payment_id,
        signature=provider.sign(payload.provider_order_id, payment_id),
    )


@router.post("/verify", response_model=OrderOut)
async def verify_payment(payload: VerifyPaymentIn, db: DbSession) -> OrderOut:
    order = await db.scalar(
        select(Order)
        .where(Order.provider_order_id == payload.provider_order_id)
        .options(selectinload(Order.items))
    )
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.status == OrderStatus.PAID:
        # A gateway can fire its callback more than once; do not double-decrement.
        return _serialize_order(order)

    try:
        valid = get_provider().verify(
            payload.provider_order_id,
            payload.provider_payment_id,
            payload.signature,
        )
    except PaymentError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    if not valid:
        order.status = OrderStatus.FAILED
        await db.commit()
        raise HTTPException(
            status_code=400, detail="Payment signature verification failed"
        )

    order.status = OrderStatus.PAID
    order.provider_payment_id = payload.provider_payment_id
    order.paid_at = datetime.now(UTC)

    # Decrement atomically in the database rather than read-modify-write in
    # Python. Two callbacks arriving at once would otherwise both read the same
    # starting value and one decrement would be lost.
    #
    # The `stock_qty >= quantity` guard means the row can never go negative. If
    # it does not match there was not enough stock — but the customer has
    # already paid at this point, so refusing is not an option. Record it loudly
    # instead: that order needs a human to restock, refund, or apologise.
    for item in order.items:
        if item.variant_id is None:
            continue

        result = await db.execute(
            update(ProductVariant)
            .where(
                ProductVariant.id == item.variant_id,
                ProductVariant.stock_qty >= item.quantity,
            )
            .values(stock_qty=ProductVariant.stock_qty - item.quantity)
        )

        if result.rowcount == 0:
            logger.error(
                "OVERSOLD: order %s paid for %d x %s (variant %s) but stock was "
                "insufficient. Stock left unchanged; this order needs manual "
                "attention.",
                order.order_number,
                item.quantity,
                item.sku,
                item.variant_id,
            )

    # Clear the cart so a refresh does not re-show paid-for items.
    cart = None
    if order.cart_token:
        cart = await db.scalar(
            select(Cart)
            .where(Cart.token == order.cart_token)
            .options(selectinload(Cart.items))
        )
    if cart is not None:
        for item in list(cart.items):
            await db.delete(item)

    await db.commit()
    await db.refresh(order, attribute_names=["items"])
    return _serialize_order(order)


@router.get("/orders/{order_number}", response_model=OrderOut)
async def get_order(order_number: str, db: DbSession) -> OrderOut:
    order = await db.scalar(
        select(Order)
        .where(Order.order_number == order_number)
        .options(selectinload(Order.items))
    )
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return _serialize_order(order)
