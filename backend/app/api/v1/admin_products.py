"""Catalog management. Every route here requires a signed-in admin.

The guard is applied at the router level rather than per-endpoint, so a new
route added later is protected by default instead of by remembering to.
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import CurrentAdmin, require_admin
from app.core.database import get_db
from app.models.order import OrderItem
from app.models.product import Product, ProductVariant
from app.schemas.admin_product import ProductIn, ProductPatch, VariantIn
from app.schemas.product import ProductOut

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/admin/products",
    tags=["admin"],
    dependencies=[Depends(require_admin)],
)

DbSession = Annotated[AsyncSession, Depends(get_db)]


async def _load(db: AsyncSession, product_id: int) -> Product:
    product = await db.scalar(
        select(Product)
        .where(Product.id == product_id)
        .options(selectinload(Product.variants))
        .execution_options(populate_existing=True)
    )
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


async def _apply_variants(
    db: AsyncSession, product: Product, incoming: list[VariantIn]
) -> None:
    """Replace the product's variants with the given list.

    Variants carrying an `id` are updated in place; the rest are created. Any
    existing variant not present in the list is deleted. Updating rather than
    delete-and-recreate matters: order_items reference variant ids, and
    recreating them would orphan that history.

    The current variants are fetched with an explicit query rather than by
    reading `product.variants`. Touching that relationship on a freshly flushed
    object triggers a lazy load, which raises MissingGreenlet inside an async
    session.
    """
    current = (
        await db.scalars(
            select(ProductVariant).where(ProductVariant.product_id == product.id)
        )
    ).all()
    existing = {v.id: v for v in current}
    keep = {spec.id for spec in incoming if spec.id is not None and spec.id in existing}

    # Removals first, flushed before anything is inserted. SKUs are unique, and
    # replacing a variant while reusing its SKU is a normal thing to do — if the
    # insert went first it would collide with the row about to be deleted.
    removed = [v for vid, v in existing.items() if vid not in keep]
    if removed:
        for variant in removed:
            await db.delete(variant)
        await db.flush()

    for spec in incoming:
        if spec.id is not None and spec.id in existing:
            variant = existing[spec.id]
        else:
            variant = ProductVariant(product_id=product.id)
            db.add(variant)

        variant.size_grams = spec.size_grams
        variant.sku = spec.sku
        variant.price_paise = spec.price_paise
        variant.compare_at_price_paise = spec.compare_at_price_paise
        variant.stock_qty = spec.stock_qty

    await db.flush()


@router.get("", response_model=list[ProductOut])
async def list_all(db: DbSession) -> list[ProductOut]:
    """Every product, including inactive ones the storefront hides."""
    products = (
        await db.scalars(
            select(Product).options(selectinload(Product.variants)).order_by(Product.id)
        )
    ).unique().all()
    return [ProductOut.model_validate(p) for p in products]


@router.post("", response_model=ProductOut, status_code=status.HTTP_201_CREATED)
async def create_product(
    payload: ProductIn, db: DbSession, admin: CurrentAdmin
) -> ProductOut:
    product = Product(
        slug=payload.slug,
        name=payload.name,
        description=payload.description,
        bean_type=payload.bean_type,
        roast_level=payload.roast_level,
        grind=payload.grind,
        flavour=payload.flavour,
        origin=payload.origin,
        tasting_notes=payload.tasting_notes,
        image_url=payload.image_url,
        is_active=payload.is_active,
        is_bestseller=payload.is_bestseller,
    )
    db.add(product)

    try:
        await db.flush()
        await _apply_variants(db, product, payload.variants)
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        # Almost always a duplicate slug or SKU. Say which, rather than 500.
        raise HTTPException(
            status_code=409,
            detail="A product with that slug, or a variant with that SKU, already exists.",
        ) from exc

    logger.info("admin %s created product %s", admin.email, product.slug)
    return ProductOut.model_validate(await _load(db, product.id))


@router.patch("/{product_id}", response_model=ProductOut)
async def update_product(
    product_id: int, payload: ProductPatch, db: DbSession, admin: CurrentAdmin
) -> ProductOut:
    product = await _load(db, product_id)

    fields = payload.model_dump(exclude_unset=True, exclude={"variants"})
    for key, value in fields.items():
        setattr(product, key, value)

    # _apply_variants flushes, so it belongs inside the try — otherwise a
    # duplicate SKU surfaces as an unhandled 500 instead of a clear 409.
    try:
        if payload.variants is not None:
            await _apply_variants(db, product, payload.variants)
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=409, detail="That SKU is already used by another variant."
        ) from exc

    logger.info("admin %s updated product %s", admin.email, product.slug)
    return ProductOut.model_validate(await _load(db, product_id))


@router.delete("/{product_id}", status_code=status.HTTP_200_OK)
async def delete_product(
    product_id: int, db: DbSession, admin: CurrentAdmin, force: bool = False
) -> dict[str, str]:
    """Hide a product, or permanently delete one that was never ordered.

    Deleting a product that appears in past orders would rewrite history, so by
    default this deactivates instead — the product vanishes from the storefront
    while the order records stay intact and truthful. `force=true` permanently
    deletes, and is refused outright once the product has been sold.
    """
    product = await _load(db, product_id)

    variant_ids = [v.id for v in product.variants]
    sold = 0
    if variant_ids:
        sold = (
            await db.scalar(
                select(func.count())
                .select_from(OrderItem)
                .where(OrderItem.variant_id.in_(variant_ids))
            )
        ) or 0

    if force and sold:
        raise HTTPException(
            status_code=409,
            detail=(
                f"This product appears in {sold} past order item(s) and cannot be "
                "permanently deleted without rewriting order history. Deactivate "
                "it instead — it will disappear from the shop and keep its records."
            ),
        )

    if force:
        await db.delete(product)
        await db.commit()
        logger.info("admin %s deleted product %s", admin.email, product.slug)
        return {"status": "deleted", "detail": f"'{product.name}' was deleted."}

    product.is_active = False
    await db.commit()
    logger.info("admin %s deactivated product %s", admin.email, product.slug)
    return {
        "status": "deactivated",
        "detail": f"'{product.name}' is now hidden from the shop.",
    }
