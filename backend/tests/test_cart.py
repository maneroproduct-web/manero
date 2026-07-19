import pytest


async def _variant_id(client, slug: str) -> int:
    r = await client.get(f"/api/v1/products/{slug}")
    return r.json()["variants"][0]["id"]


@pytest.fixture
async def cart_token(client):
    r = await client.post("/api/v1/carts")
    assert r.status_code == 201
    return r.json()["token"]


async def test_add_item_computes_totals_server_side(client, catalog, cart_token):
    vid = await _variant_id(client, "dark-arabica")
    r = await client.post(
        f"/api/v1/carts/{cart_token}/items", json={"variant_id": vid, "quantity": 2}
    )
    body = r.json()
    assert body["item_count"] == 2
    assert body["subtotal_paise"] == 80000  # 2 x 40000


async def test_adding_same_variant_bumps_quantity(client, catalog, cart_token):
    vid = await _variant_id(client, "dark-arabica")
    await client.post(f"/api/v1/carts/{cart_token}/items", json={"variant_id": vid})
    r = await client.post(f"/api/v1/carts/{cart_token}/items", json={"variant_id": vid})
    body = r.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["quantity"] == 2


async def test_cannot_exceed_stock(client, catalog, cart_token):
    vid = await _variant_id(client, "hazelnut-instant")  # stock 2
    r = await client.post(
        f"/api/v1/carts/{cart_token}/items", json={"variant_id": vid, "quantity": 3}
    )
    assert r.status_code == 409


async def test_quantity_zero_removes_line(client, catalog, cart_token):
    vid = await _variant_id(client, "dark-arabica")
    added = await client.post(
        f"/api/v1/carts/{cart_token}/items", json={"variant_id": vid}
    )
    item_id = added.json()["items"][0]["id"]

    r = await client.patch(
        f"/api/v1/carts/{cart_token}/items/{item_id}", json={"quantity": 0}
    )
    assert r.json()["items"] == []
    assert r.json()["subtotal_paise"] == 0


async def test_cart_persists_across_requests(client, catalog, cart_token):
    """The token is all the client keeps; refetching must return the same cart."""
    vid = await _variant_id(client, "dark-arabica")
    await client.post(f"/api/v1/carts/{cart_token}/items", json={"variant_id": vid})

    r = await client.get(f"/api/v1/carts/{cart_token}")
    assert r.json()["item_count"] == 1


async def test_unknown_cart_404s(client):
    r = await client.get("/api/v1/carts/deadbeef")
    assert r.status_code == 404


async def test_shipping_is_free_above_threshold(client, catalog, cart_token):
    # 2 x 40000 = 80000 paise, above the 59900 free-shipping threshold.
    vid = await _variant_id(client, "dark-arabica")
    r = await client.post(
        f"/api/v1/carts/{cart_token}/items", json={"variant_id": vid, "quantity": 2}
    )
    assert r.json()["shipping_paise"] == 0


async def test_shipping_charged_below_threshold(client, catalog, cart_token):
    vid = await _variant_id(client, "hazelnut-instant")  # 20000 paise
    r = await client.post(f"/api/v1/carts/{cart_token}/items", json={"variant_id": vid})
    body = r.json()
    assert body["shipping_paise"] == 4900
    assert body["total_paise"] == 24900
