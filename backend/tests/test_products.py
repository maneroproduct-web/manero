async def test_lists_active_products(client, catalog):
    r = await client.get("/api/v1/products")
    assert r.status_code == 200
    body = r.json()
    assert body["total"] == 3
    assert len(body["items"]) == 3


async def test_filter_by_single_dimension(client, catalog):
    r = await client.get("/api/v1/products", params={"bean_type": "arabica"})
    slugs = {p["slug"] for p in r.json()["items"]}
    assert slugs == {"dark-arabica", "light-arabica"}


async def test_filters_are_or_within_and_and_across_dimensions(client, catalog):
    # Arabica AND (dark OR light) -> both arabicas, not the blend.
    r = await client.get(
        "/api/v1/products",
        params=[("bean_type", "arabica"), ("roast_level", "dark"), ("roast_level", "light")],
    )
    slugs = {p["slug"] for p in r.json()["items"]}
    assert slugs == {"dark-arabica", "light-arabica"}


def _slugs(body):
    return [p["slug"] for p in body["items"]]


async def test_sort_by_price_uses_cheapest_variant(client, catalog):
    asc = await client.get("/api/v1/products", params={"sort": "price_asc"})
    assert _slugs(asc.json()) == ["hazelnut-instant", "dark-arabica", "light-arabica"]

    desc = await client.get("/api/v1/products", params={"sort": "price_desc"})
    assert _slugs(desc.json()) == ["light-arabica", "dark-arabica", "hazelnut-instant"]


async def test_facets_report_counts(client, catalog):
    r = await client.get("/api/v1/products/facets")
    assert r.status_code == 200
    facets = r.json()
    counts = {f["value"]: f["count"] for f in facets["bean_type"]}
    assert counts == {"arabica": 2, "blend": 1}
    labels = {f["value"]: f["label"] for f in facets["grind"]}
    assert labels["instant"] == "Instant"


async def test_facets_route_not_shadowed_by_slug_route(client, catalog):
    """'/products/facets' must hit the facets handler, not be read as a slug."""
    r = await client.get("/api/v1/products/facets")
    assert "bean_type" in r.json()


async def test_product_detail_and_404(client, catalog):
    r = await client.get("/api/v1/products/dark-arabica")
    assert r.status_code == 200
    assert r.json()["variants"][0]["price_paise"] == 40000

    missing = await client.get("/api/v1/products/nope")
    assert missing.status_code == 404


async def test_pagination(client, catalog):
    r = await client.get("/api/v1/products", params={"page_size": 2, "page": 2})
    body = r.json()
    assert body["total"] == 3
    assert body["total_pages"] == 2
    assert len(body["items"]) == 1
