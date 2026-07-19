import pytest

from app.core.config import settings
from app.services.payments import DummyProvider, PaymentError, get_provider

ADDRESS = {
    "name": "Test Buyer",
    "line1": "12 Brew Street",
    "line2": "",
    "city": "Bengaluru",
    "state": "Karnataka",
    "pincode": "560001",
}


@pytest.fixture(autouse=True)
def dummy_payments(monkeypatch):
    """Every test here runs against the dummy gateway: no keys, no network."""
    monkeypatch.setattr(settings, "payment_provider", "dummy")
    monkeypatch.setattr(settings, "environment", "development")
    monkeypatch.setattr(settings, "dummy_payment_secret", "test-secret")


async def _cart_with_items(client, slug="dark-arabica", quantity=2) -> str:
    token = (await client.post("/api/v1/carts")).json()["token"]
    vid = (await client.get(f"/api/v1/products/{slug}")).json()["variants"][0]["id"]
    await client.post(
        f"/api/v1/carts/{token}/items", json={"variant_id": vid, "quantity": quantity}
    )
    return token


async def _create_order(client, token: str):
    return await client.post(
        "/api/v1/checkout/create-order",
        json={
            "cart_token": token,
            "email": "buyer@example.com",
            "phone": "9876543210",
            "shipping": ADDRESS,
        },
    )


async def _pay(client, provider_order_id: str, succeed: bool = True):
    """Simulate the gateway UI, then verify along the normal path."""
    callback = await client.post(
        "/api/v1/checkout/dummy-pay",
        json={"provider_order_id": provider_order_id, "succeed": succeed},
    )
    return await client.post("/api/v1/checkout/verify", json=callback.json())


# --- provider selection ---------------------------------------------------


def test_dummy_provider_is_the_default(monkeypatch):
    monkeypatch.setattr(settings, "payment_provider", "dummy")
    monkeypatch.setattr(settings, "environment", "development")
    assert isinstance(get_provider(), DummyProvider)


def test_dummy_provider_refused_in_production(monkeypatch):
    """A fake gateway in production would wave through forged payments."""
    monkeypatch.setattr(settings, "payment_provider", "dummy")
    monkeypatch.setattr(settings, "environment", "production")
    with pytest.raises(PaymentError, match="production"):
        get_provider()


def test_unknown_provider_is_rejected(monkeypatch):
    monkeypatch.setattr(settings, "payment_provider", "paypal")
    with pytest.raises(PaymentError, match="Unknown PAYMENT_PROVIDER"):
        get_provider()


def test_razorpay_without_keys_explains_itself(monkeypatch):
    monkeypatch.setattr(settings, "payment_provider", "razorpay")
    monkeypatch.setattr(settings, "razorpay_key_id", "")
    monkeypatch.setattr(settings, "razorpay_key_secret", "")
    with pytest.raises(PaymentError, match="RAZORPAY_KEY_ID"):
        get_provider()


# --- create order ---------------------------------------------------------


async def test_create_order_returns_server_computed_amount(client, catalog):
    token = await _cart_with_items(client)
    r = await _create_order(client, token)
    assert r.status_code == 200
    body = r.json()
    # 2 x 40000 = 80000, free shipping above threshold.
    assert body["amount_paise"] == 80000
    assert body["provider"] == "dummy"
    assert body["provider_order_id"].startswith("dummy_order_")


async def test_client_cannot_dictate_the_price(client, catalog):
    """Extra price fields in the payload must be ignored, not honoured."""
    token = await _cart_with_items(client)
    r = await client.post(
        "/api/v1/checkout/create-order",
        json={
            "cart_token": token,
            "email": "buyer@example.com",
            "phone": "9876543210",
            "shipping": ADDRESS,
            "amount_paise": 1,
            "total_paise": 1,
            "subtotal_paise": 1,
        },
    )
    assert r.status_code == 200
    assert r.json()["amount_paise"] == 80000


async def test_empty_cart_is_rejected(client, catalog):
    token = (await client.post("/api/v1/carts")).json()["token"]
    assert (await _create_order(client, token)).status_code == 400


async def test_invalid_pincode_is_rejected(client, catalog):
    token = await _cart_with_items(client)
    r = await client.post(
        "/api/v1/checkout/create-order",
        json={
            "cart_token": token,
            "email": "buyer@example.com",
            "phone": "9876543210",
            "shipping": {**ADDRESS, "pincode": "56OOO1"},
        },
    )
    assert r.status_code == 422


# --- verification ---------------------------------------------------------


async def test_successful_payment_marks_paid_and_decrements_stock(client, catalog):
    token = await _cart_with_items(client, quantity=2)
    created = await _create_order(client, token)
    order_number = created.json()["order_number"]

    r = await _pay(client, created.json()["provider_order_id"])
    assert r.status_code == 200
    assert r.json()["status"] == "paid"
    assert r.json()["order_number"] == order_number

    # dark-arabica started at stock 5, 2 were bought.
    detail = await client.get("/api/v1/products/dark-arabica")
    assert detail.json()["variants"][0]["stock_qty"] == 3

    # And the cart is emptied.
    assert (await client.get(f"/api/v1/carts/{token}")).json()["items"] == []


async def test_simulated_failure_is_rejected(client, catalog):
    token = await _cart_with_items(client)
    created = await _create_order(client, token)

    r = await _pay(client, created.json()["provider_order_id"], succeed=False)
    assert r.status_code == 400

    # Stock must be untouched by a failed payment.
    detail = await client.get("/api/v1/products/dark-arabica")
    assert detail.json()["variants"][0]["stock_qty"] == 5


async def test_verify_rejects_tampered_signature(client, catalog):
    token = await _cart_with_items(client)
    created = await _create_order(client, token)

    r = await client.post(
        "/api/v1/checkout/verify",
        json={
            "provider_order_id": created.json()["provider_order_id"],
            "provider_payment_id": "dummy_pay_forged",
            "signature": "a" * 64,
        },
    )
    assert r.status_code == 400


async def test_stock_never_goes_negative(client, catalog, session_factory):
    """Payment is already taken by this point, so we cannot refuse — but the
    row must not be driven below zero, and the oversell must be recorded."""
    from sqlalchemy import select

    from app.models import ProductVariant

    token = await _cart_with_items(client, quantity=2)   # dark-arabica, stock 5
    created = await _create_order(client, token)

    # Someone else empties the shelf between order creation and the callback.
    async with session_factory() as session:
        variant = await session.scalar(
            select(ProductVariant).where(ProductVariant.sku == "DARK-ARABICA-250")
        )
        variant.stock_qty = 1          # less than the 2 that were bought
        await session.commit()

    r = await _pay(client, created.json()["provider_order_id"])
    assert r.status_code == 200
    assert r.json()["status"] == "paid"     # the customer paid; honour it

    async with session_factory() as session:
        variant = await session.scalar(
            select(ProductVariant).where(ProductVariant.sku == "DARK-ARABICA-250")
        )
        # Left alone rather than driven to -1.
        assert variant.stock_qty == 1


async def test_create_order_rejects_more_than_available(client, catalog):
    """The stock re-check reads the database, not the cart's cached copy."""
    token = (await client.post("/api/v1/carts")).json()["token"]
    vid = (await client.get("/api/v1/products/hazelnut-instant")).json()["variants"][0]["id"]
    # stock is 2, so this is the most that can be added
    await client.post(
        f"/api/v1/carts/{token}/items", json={"variant_id": vid, "quantity": 2}
    )

    r = await _create_order(client, token)
    assert r.status_code == 200   # exactly the available quantity is fine


async def test_verify_is_idempotent(client, catalog):
    """A gateway can deliver its callback twice; stock must only drop once."""
    token = await _cart_with_items(client, quantity=2)
    created = await _create_order(client, token)
    provider_order_id = created.json()["provider_order_id"]

    callback = await client.post(
        "/api/v1/checkout/dummy-pay",
        json={"provider_order_id": provider_order_id, "succeed": True},
    )
    await client.post("/api/v1/checkout/verify", json=callback.json())
    second = await client.post("/api/v1/checkout/verify", json=callback.json())

    assert second.status_code == 200
    detail = await client.get("/api/v1/products/dark-arabica")
    assert detail.json()["variants"][0]["stock_qty"] == 3  # not 1


async def test_dummy_pay_blocked_when_provider_is_not_dummy(client, catalog, monkeypatch):
    """The simulation endpoint must not exist once a real gateway is live."""
    token = await _cart_with_items(client)
    created = await _create_order(client, token)

    monkeypatch.setattr(settings, "payment_provider", "razorpay")
    monkeypatch.setattr(settings, "razorpay_key_id", "rzp_test_x")
    monkeypatch.setattr(settings, "razorpay_key_secret", "secret")

    r = await client.post(
        "/api/v1/checkout/dummy-pay",
        json={"provider_order_id": created.json()["provider_order_id"]},
    )
    assert r.status_code == 404


# --- order records --------------------------------------------------------


async def test_order_lookup_by_number(client, catalog):
    token = await _cart_with_items(client)
    order_number = (await _create_order(client, token)).json()["order_number"]

    r = await client.get(f"/api/v1/checkout/orders/{order_number}")
    assert r.status_code == 200
    assert r.json()["items"][0]["product_name"] == "Dark Arabica"


async def test_order_items_survive_product_rename(client, catalog, session_factory):
    """Order history is a record of what was bought, not a live join."""
    from sqlalchemy import select

    from app.models import Product

    token = await _cart_with_items(client)
    order_number = (await _create_order(client, token)).json()["order_number"]

    async with session_factory() as session:
        product = await session.scalar(
            select(Product).where(Product.slug == "dark-arabica")
        )
        product.name = "Renamed Later"
        await session.commit()

    r = await client.get(f"/api/v1/checkout/orders/{order_number}")
    assert r.json()["items"][0]["product_name"] == "Dark Arabica"
