import pytest
import pytest_asyncio
from sqlalchemy import select

from app.core.security import hash_password
from app.models import AdminUser, Product

PASSWORD = "correct-horse-battery"

NEW_PRODUCT = {
    "slug": "test-blend",
    "name": "Test Blend",
    "description": "For testing.",
    "bean_type": "blend",
    "roast_level": "medium",
    "grind": "filter",
    "flavour": "original",
    "origin": "Nowhere",
    "tasting_notes": "Cardboard",
    "image_url": "",
    "is_active": True,
    "is_bestseller": False,
    "variants": [
        {"size_grams": 250, "sku": "TEST-250", "price_paise": 30000, "stock_qty": 10}
    ],
}


@pytest_asyncio.fixture
async def admin(session_factory):
    async with session_factory() as session:
        session.add(
            AdminUser(
                email="staff@manero.in",
                name="Staff",
                password_hash=hash_password(PASSWORD),
            )
        )
        await session.commit()


@pytest_asyncio.fixture
async def token(client, admin) -> str:
    r = await client.post(
        "/api/v1/auth/login",
        json={"email": "staff@manero.in", "password": PASSWORD},
    )
    assert r.status_code == 200
    return r.json()["access_token"]


def auth(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


# --- login ----------------------------------------------------------------


async def test_login_returns_a_token(client, admin):
    r = await client.post(
        "/api/v1/auth/login",
        json={"email": "staff@manero.in", "password": PASSWORD},
    )
    assert r.status_code == 200
    assert r.json()["access_token"]
    assert r.json()["admin"]["email"] == "staff@manero.in"


async def test_wrong_password_is_refused(client, admin):
    r = await client.post(
        "/api/v1/auth/login",
        json={"email": "staff@manero.in", "password": "wrong"},
    )
    assert r.status_code == 401


@pytest.mark.parametrize(
    "payload",
    [
        {"email": "staff@manero.in", "password": "wrong"},
        {"email": "nobody@manero.in", "password": PASSWORD},
    ],
)
async def test_failures_are_indistinguishable(client, admin, payload):
    """Wrong password and unknown account must look identical, or the login
    form becomes a way to discover which addresses are staff accounts."""
    r = await client.post("/api/v1/auth/login", json=payload)
    assert r.status_code == 401
    assert r.json()["detail"] == "Email or password is incorrect."


async def test_deactivated_admin_cannot_log_in(client, admin, session_factory):
    async with session_factory() as session:
        user = await session.scalar(select(AdminUser))
        user.is_active = False
        await session.commit()

    r = await client.post(
        "/api/v1/auth/login",
        json={"email": "staff@manero.in", "password": PASSWORD},
    )
    assert r.status_code == 401


async def test_password_is_never_stored_in_plain_text(client, admin, session_factory):
    async with session_factory() as session:
        user = await session.scalar(select(AdminUser))
    assert PASSWORD not in user.password_hash
    assert user.password_hash.startswith("$argon2")


# --- the guard ------------------------------------------------------------


@pytest.mark.parametrize(
    ("method", "path"),
    [
        ("get", "/api/v1/admin/products"),
        ("post", "/api/v1/admin/products"),
        ("patch", "/api/v1/admin/products/1"),
        ("delete", "/api/v1/admin/products/1"),
    ],
)
async def test_admin_routes_refuse_anonymous_access(client, catalog, method, path):
    # request() rather than client.get()/delete() — those two do not accept a
    # json body in httpx.
    r = await client.request(method.upper(), path, json={})
    assert r.status_code == 401


async def test_garbage_token_is_refused(client, catalog):
    r = await client.get("/api/v1/admin/products", headers=auth("not-a-real-token"))
    assert r.status_code == 401


async def test_token_for_deleted_admin_stops_working(client, token, session_factory):
    """The guard re-reads the user each request, so revoking access is immediate
    rather than waiting for the token to expire."""
    async with session_factory() as session:
        user = await session.scalar(select(AdminUser))
        user.is_active = False
        await session.commit()

    r = await client.get("/api/v1/admin/products", headers=auth(token))
    assert r.status_code == 401


async def test_me_returns_the_signed_in_admin(client, token):
    r = await client.get("/api/v1/auth/me", headers=auth(token))
    assert r.status_code == 200
    assert r.json()["email"] == "staff@manero.in"


# --- create / update / delete ---------------------------------------------


async def test_create_product(client, token, session_factory):
    r = await client.post("/api/v1/admin/products", json=NEW_PRODUCT, headers=auth(token))
    assert r.status_code == 201
    assert r.json()["slug"] == "test-blend"
    assert len(r.json()["variants"]) == 1

    # And it is immediately visible on the storefront.
    shop = await client.get("/api/v1/products/test-blend")
    assert shop.status_code == 200


async def test_duplicate_slug_is_rejected(client, token):
    await client.post("/api/v1/admin/products", json=NEW_PRODUCT, headers=auth(token))
    again = await client.post(
        "/api/v1/admin/products",
        json={**NEW_PRODUCT, "variants": [{**NEW_PRODUCT["variants"][0], "sku": "OTHER"}]},
        headers=auth(token),
    )
    assert again.status_code == 409


async def test_invalid_slug_is_rejected(client, token):
    r = await client.post(
        "/api/v1/admin/products",
        json={**NEW_PRODUCT, "slug": "not a slug!"},
        headers=auth(token),
    )
    assert r.status_code == 422


async def test_duplicate_sizes_are_rejected(client, token):
    r = await client.post(
        "/api/v1/admin/products",
        json={
            **NEW_PRODUCT,
            "variants": [
                {"size_grams": 250, "sku": "A", "price_paise": 100, "stock_qty": 1},
                {"size_grams": 250, "sku": "B", "price_paise": 200, "stock_qty": 1},
            ],
        },
        headers=auth(token),
    )
    assert r.status_code == 422


async def test_update_product(client, token, catalog, session_factory):
    async with session_factory() as session:
        product = await session.scalar(select(Product).where(Product.slug == "dark-arabica"))
        pid = product.id

    r = await client.patch(
        f"/api/v1/admin/products/{pid}",
        json={"name": "Renamed Roast", "is_bestseller": False},
        headers=auth(token),
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Renamed Roast"
    # Untouched fields survive a partial update.
    assert r.json()["origin"] == "Test"


async def test_update_replaces_variants_and_keeps_ids(client, token, catalog, session_factory):
    async with session_factory() as session:
        product = await session.scalar(select(Product).where(Product.slug == "dark-arabica"))
        pid, vid = product.id, product.variants[0].id

    r = await client.patch(
        f"/api/v1/admin/products/{pid}",
        json={
            "variants": [
                {"id": vid, "size_grams": 250, "sku": "DA-250", "price_paise": 55000, "stock_qty": 7},
                {"size_grams": 500, "sku": "DA-500", "price_paise": 99000, "stock_qty": 3},
            ]
        },
        headers=auth(token),
    )
    assert r.status_code == 200
    variants = sorted(r.json()["variants"], key=lambda v: v["size_grams"])
    assert len(variants) == 2
    # The existing row was updated, not recreated — order history still points at it.
    assert variants[0]["id"] == vid
    assert variants[0]["price_paise"] == 55000


async def test_replacing_a_variant_can_reuse_its_sku(client, token, catalog, session_factory):
    """Sending a variant list without ids replaces the lot.

    Reusing a SKU while doing so is ordinary — same size, repriced. It only
    works if removals are flushed before inserts; otherwise the new row collides
    with the old one that is about to be deleted, and the unique index fires.
    """
    async with session_factory() as session:
        product = await session.scalar(select(Product).where(Product.slug == "dark-arabica"))
        pid = product.id
        old_sku = product.variants[0].sku

    r = await client.patch(
        f"/api/v1/admin/products/{pid}",
        json={
            "variants": [
                {"size_grams": 250, "sku": old_sku, "price_paise": 50000, "stock_qty": 2}
            ]
        },
        headers=auth(token),
    )
    assert r.status_code == 200, r.text
    assert len(r.json()["variants"]) == 1
    assert r.json()["variants"][0]["sku"] == old_sku
    assert r.json()["variants"][0]["price_paise"] == 50000


async def test_skus_are_normalised_to_uppercase(client, token):
    """Lower-case input is stored upper-case, so 'abc-1' and 'ABC-1' cannot
    both exist and quietly refer to different stock."""
    r = await client.post(
        "/api/v1/admin/products",
        json={**NEW_PRODUCT, "variants": [{**NEW_PRODUCT["variants"][0], "sku": "lower-case-sku"}]},
        headers=auth(token),
    )
    assert r.status_code == 201
    assert r.json()["variants"][0]["sku"] == "LOWER-CASE-SKU"


async def test_duplicate_sku_within_one_request_is_a_clean_error(client, token, catalog, session_factory):
    """A genuine conflict must be a 409 with a readable message, not a 500."""
    async with session_factory() as session:
        dark = await session.scalar(select(Product).where(Product.slug == "dark-arabica"))
        light = await session.scalar(select(Product).where(Product.slug == "light-arabica"))
        pid, other_sku = dark.id, light.variants[0].sku

    r = await client.patch(
        f"/api/v1/admin/products/{pid}",
        json={
            "variants": [
                {"size_grams": 250, "sku": other_sku, "price_paise": 50000, "stock_qty": 2}
            ]
        },
        headers=auth(token),
    )
    assert r.status_code == 409
    assert "sku" in r.json()["detail"].lower()


async def test_delete_deactivates_by_default(client, token, catalog, session_factory):
    async with session_factory() as session:
        product = await session.scalar(select(Product).where(Product.slug == "dark-arabica"))
        pid = product.id

    r = await client.delete(f"/api/v1/admin/products/{pid}", headers=auth(token))
    assert r.status_code == 200
    assert r.json()["status"] == "deactivated"

    # Gone from the shop, still in the database.
    assert (await client.get("/api/v1/products/dark-arabica")).status_code == 404
    async with session_factory() as session:
        assert await session.scalar(select(Product).where(Product.id == pid)) is not None


async def test_force_delete_removes_an_unsold_product(client, token, session_factory):
    created = await client.post(
        "/api/v1/admin/products", json=NEW_PRODUCT, headers=auth(token)
    )
    pid = created.json()["id"]

    r = await client.delete(f"/api/v1/admin/products/{pid}?force=true", headers=auth(token))
    assert r.status_code == 200
    assert r.json()["status"] == "deleted"

    async with session_factory() as session:
        assert await session.scalar(select(Product).where(Product.id == pid)) is None


async def test_force_delete_refused_once_product_has_been_ordered(client, token, catalog):
    """Deleting a sold product would rewrite what past orders say was bought."""
    # Buy one.
    cart_token = (await client.post("/api/v1/carts")).json()["token"]
    detail = (await client.get("/api/v1/products/dark-arabica")).json()
    await client.post(
        f"/api/v1/carts/{cart_token}/items",
        json={"variant_id": detail["variants"][0]["id"], "quantity": 1},
    )
    await client.post(
        "/api/v1/checkout/create-order",
        json={
            "cart_token": cart_token,
            "email": "buyer@example.com",
            "phone": "9876543210",
            "shipping": {
                "name": "Buyer", "line1": "1 Road", "line2": "",
                "city": "Bengaluru", "state": "Karnataka", "pincode": "560001",
            },
        },
    )

    r = await client.delete(
        f"/api/v1/admin/products/{detail['id']}?force=true", headers=auth(token)
    )
    assert r.status_code == 409
    assert "order" in r.json()["detail"].lower()


async def test_admin_list_includes_inactive_products(client, token, catalog, session_factory):
    async with session_factory() as session:
        product = await session.scalar(select(Product).where(Product.slug == "dark-arabica"))
        product.is_active = False
        await session.commit()

    shop = await client.get("/api/v1/products")
    admin_list = await client.get("/api/v1/admin/products", headers=auth(token))

    assert shop.json()["total"] == 2
    assert len(admin_list.json()) == 3
