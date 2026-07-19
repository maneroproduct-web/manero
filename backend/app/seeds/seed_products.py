"""Seed the catalog with placeholder Manero products.

Run from backend/:   python -m app.seeds.seed_products

Idempotent: products are matched by slug and updated in place, so re-running
does not duplicate rows. Swap this data for real SKUs when they exist.
"""

import sys

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models import Product, ProductVariant
from app.models.enums import BeanType, Flavour, Grind, RoastLevel

# Placeholder imagery until real product photography exists.
IMG = "https://images.unsplash.com/photo-{id}?auto=format&fit=crop&w=800&q=80"

PRODUCTS = [
    {
        "slug": "signature-arabica-medium-filter",
        "name": "Manero Signature Arabica — Medium Roast",
        "description": (
            "Our house filter coffee. Single-origin Arabica from the Chikmagalur "
            "hills, roasted medium to keep the sweetness forward without losing "
            "body. Ground for South Indian filter and pour-over alike."
        ),
        "bean_type": BeanType.ARABICA,
        "roast_level": RoastLevel.MEDIUM,
        "grind": Grind.FILTER,
        "flavour": Flavour.ORIGINAL,
        "origin": "Chikmagalur, Karnataka",
        "tasting_notes": "Milk chocolate, toasted almond, a soft citrus finish",
        "image": "1447933601403-0c6688de566e",
        "bestseller": True,
        "variants": [(250, 44900, 49900), (500, 84900, 94900), (1000, 159900, None)],
    },
    {
        "slug": "highland-arabica-light-filter",
        "name": "Highland Arabica — Light Roast",
        "description": (
            "Picked at 1,600m and roasted light to protect the delicate floral "
            "top notes. Bright, tea-like and clean — best brewed as pour-over."
        ),
        "bean_type": BeanType.ARABICA,
        "roast_level": RoastLevel.LIGHT,
        "grind": Grind.FILTER,
        "flavour": Flavour.ORIGINAL,
        "origin": "Araku Valley, Andhra Pradesh",
        "tasting_notes": "Jasmine, green apple, honey",
        "image": "1495474472287-4d71bcdd2085",
        "bestseller": False,
        "variants": [(250, 54900, None), (500, 99900, 109900)],
    },
    {
        "slug": "midnight-arabica-dark-filter",
        "name": "Midnight Arabica — Dark Roast",
        "description": (
            "Roasted long and deep for people who take their coffee strong and "
            "their mornings seriously. Low acidity, heavy body, cuts through milk."
        ),
        "bean_type": BeanType.ARABICA,
        "roast_level": RoastLevel.DARK,
        "grind": Grind.FILTER,
        "flavour": Flavour.ORIGINAL,
        "origin": "Coorg, Karnataka",
        "tasting_notes": "Dark cocoa, molasses, roasted walnut",
        "image": "1509042239860-f550ce710b93",
        "bestseller": True,
        "variants": [(250, 42900, None), (500, 79900, 89900), (1000, 149900, None)],
    },
    {
        "slug": "espresso-blend-whole-bean",
        "name": "Manero Espresso Blend — Whole Bean",
        "description": (
            "70% Arabica for sweetness, 30% Robusta for crema and punch. "
            "Dialled in for a 1:2 ratio in 28 seconds. Grind fresh."
        ),
        "bean_type": BeanType.BLEND,
        "roast_level": RoastLevel.DARK,
        "grind": Grind.WHOLE_BEAN,
        "flavour": Flavour.ORIGINAL,
        "origin": "Karnataka & Kerala",
        "tasting_notes": "Caramelised sugar, hazelnut, dried fig",
        "image": "1442512595331-e89e73853f31",
        "bestseller": True,
        "variants": [(250, 49900, None), (500, 92900, 104900), (1000, 174900, None)],
    },
    {
        "slug": "robusta-kick-espresso",
        "name": "Robusta Kick — Espresso Grind",
        "description": (
            "Nearly double the caffeine of a straight Arabica. Thick crema, "
            "bold and unapologetic. For the second cup that has to work."
        ),
        "bean_type": BeanType.ROBUSTA,
        "roast_level": RoastLevel.DARK,
        "grind": Grind.ESPRESSO,
        "flavour": Flavour.ORIGINAL,
        "origin": "Wayanad, Kerala",
        "tasting_notes": "Bitter chocolate, black pepper, earthy depth",
        "image": "1514432324607-a09d9b4aefdd",
        "bestseller": False,
        "variants": [(250, 37900, 42900), (500, 69900, None)],
    },
    {
        "slug": "house-blend-medium-whole-bean",
        "name": "House Blend — Medium Roast Whole Bean",
        "description": (
            "The everyday bag. Balanced enough for filter, espresso or French "
            "press, forgiving if your grind is a little off."
        ),
        "bean_type": BeanType.BLEND,
        "roast_level": RoastLevel.MEDIUM,
        "grind": Grind.WHOLE_BEAN,
        "flavour": Flavour.ORIGINAL,
        "origin": "Multi-estate, South India",
        "tasting_notes": "Brown sugar, baked bread, stone fruit",
        "image": "1559056199-641a0ac8b55e",
        "bestseller": False,
        "variants": [(250, 39900, None), (500, 74900, 84900), (1000, 139900, None)],
    },
    {
        "slug": "instant-classic-original",
        "name": "Instant Classic — Original",
        "description": (
            "Freeze-dried from 100% Arabica, not spray-dried. Dissolves clean in "
            "hot or cold water in about 30 seconds. No bitterness, no sludge."
        ),
        "bean_type": BeanType.ARABICA,
        "roast_level": RoastLevel.MEDIUM,
        "grind": Grind.INSTANT,
        "flavour": Flavour.ORIGINAL,
        "origin": "Blended & freeze-dried in India",
        "tasting_notes": "Clean, rounded, mildly nutty",
        "image": "1521302080334-4bebac2763a6",
        "bestseller": True,
        "variants": [(50, 24900, 29900), (100, 44900, None), (200, 79900, 89900)],
    },
    {
        "slug": "instant-hazelnut",
        "name": "Instant Hazelnut",
        "description": (
            "Roasted hazelnut folded into our freeze-dried Arabica base. "
            "No added sugar — sweeten it your way."
        ),
        "bean_type": BeanType.ARABICA,
        "roast_level": RoastLevel.MEDIUM,
        "grind": Grind.INSTANT,
        "flavour": Flavour.HAZELNUT,
        "origin": "Blended & freeze-dried in India",
        "tasting_notes": "Toasted hazelnut, cream, cocoa",
        "image": "1572442388796-11668a67e53d",
        "bestseller": True,
        "variants": [(50, 27900, 32900), (100, 49900, None)],
    },
    {
        "slug": "instant-french-vanilla",
        "name": "Instant French Vanilla",
        "description": (
            "Smooth vanilla over a medium-roast base. Works especially well as "
            "an iced latte with cold milk and a little ice."
        ),
        "bean_type": BeanType.ARABICA,
        "roast_level": RoastLevel.MEDIUM,
        "grind": Grind.INSTANT,
        "flavour": Flavour.VANILLA,
        "origin": "Blended & freeze-dried in India",
        "tasting_notes": "Vanilla bean, custard, light caramel",
        "image": "1461023058943-07fcbe16d735",
        "bestseller": False,
        "variants": [(50, 27900, 32900), (100, 49900, None)],
    },
    {
        "slug": "instant-salted-caramel",
        "name": "Instant Salted Caramel",
        "description": (
            "Burnt-sugar caramel with just enough salt to stop it turning "
            "cloying. Our most-ordered flavoured jar."
        ),
        "bean_type": BeanType.ARABICA,
        "roast_level": RoastLevel.MEDIUM,
        "grind": Grind.INSTANT,
        "flavour": Flavour.CARAMEL,
        "origin": "Blended & freeze-dried in India",
        "tasting_notes": "Salted caramel, butterscotch, malt",
        "image": "1517701550927-30cf4ba1dba5",
        "bestseller": True,
        "variants": [(50, 27900, 32900), (100, 49900, 56900), (200, 89900, None)],
    },
    {
        "slug": "instant-mocha",
        "name": "Instant Mocha",
        "description": (
            "Coffee and cocoa in the same jar. Richer than a plain instant, "
            "lighter than a hot chocolate."
        ),
        "bean_type": BeanType.BLEND,
        "roast_level": RoastLevel.DARK,
        "grind": Grind.INSTANT,
        "flavour": Flavour.MOCHA,
        "origin": "Blended & freeze-dried in India",
        "tasting_notes": "Dark cocoa, brownie, condensed milk",
        "image": "1578314675249-a6910f80cc4e",
        "bestseller": False,
        "variants": [(50, 29900, None), (100, 54900, 62900)],
    },
    {
        "slug": "cold-brew-coarse-blend",
        "name": "Cold Brew Blend — Coarse Ground",
        "description": (
            "Ground coarse specifically for a 12–16 hour cold steep. Sweet and "
            "syrupy, none of the bitterness you get from over-extracting fine grounds."
        ),
        "bean_type": BeanType.BLEND,
        "roast_level": RoastLevel.MEDIUM,
        "grind": Grind.FILTER,
        "flavour": Flavour.ORIGINAL,
        "origin": "Chikmagalur & Wayanad",
        "tasting_notes": "Cane sugar, cherry, cocoa nib",
        "image": "1461988091159-192b6df7054f",
        "bestseller": False,
        "variants": [(250, 46900, None), (500, 87900, 97900)],
    },
]


def build_sku(slug: str, grams: int) -> str:
    prefix = "".join(w[0] for w in slug.split("-"))[:6].upper()
    return f"MNR-{prefix}-{grams}G"


def seed(session: Session) -> tuple[int, int]:
    created = updated = 0

    for spec in PRODUCTS:
        product = session.scalar(select(Product).where(Product.slug == spec["slug"]))
        if product is None:
            product = Product(slug=spec["slug"])
            session.add(product)
            created += 1
        else:
            updated += 1

        product.name = spec["name"]
        product.description = spec["description"]
        product.bean_type = spec["bean_type"]
        product.roast_level = spec["roast_level"]
        product.grind = spec["grind"]
        product.flavour = spec["flavour"]
        product.origin = spec["origin"]
        product.tasting_notes = spec["tasting_notes"]
        product.image_url = IMG.format(id=spec["image"])
        product.is_active = True
        product.is_bestseller = spec["bestseller"]

        session.flush()  # need product.id before touching variants

        existing = {v.size_grams: v for v in product.variants}
        for grams, price, compare_at in spec["variants"]:
            variant = existing.get(grams)
            if variant is None:
                variant = ProductVariant(
                    product_id=product.id,
                    size_grams=grams,
                    sku=build_sku(spec["slug"], grams),
                )
                session.add(variant)
            variant.price_paise = price
            variant.compare_at_price_paise = compare_at
            variant.stock_qty = 100

    session.commit()
    return created, updated


def main() -> int:
    engine = create_engine(settings.sync_database_url, future=True)
    with Session(engine) as session:
        created, updated = seed(session)
    print(f"Seed complete: {created} product(s) created, {updated} updated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
