from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.enums import LABELS, BeanType, Flavour, Grind, RoastLevel
from app.models.product import Product, ProductVariant
from app.schemas.product import FacetsOut, FacetValue, ProductListOut, ProductOut

router = APIRouter(prefix="/products", tags=["products"])

SortOption = Literal["featured", "price_asc", "price_desc", "newest"]

DbSession = Annotated[AsyncSession, Depends(get_db)]


def _apply_filters(
    stmt,
    bean_type: list[BeanType] | None,
    roast_level: list[RoastLevel] | None,
    grind: list[Grind] | None,
    flavour: list[Flavour] | None,
):
    """Filters are OR within a dimension, AND across dimensions.

    Picking 'light' and 'dark' shows both; adding 'arabica' narrows to Arabica
    that is either light or dark. This is what shoppers expect from facets.
    """
    if bean_type:
        stmt = stmt.where(Product.bean_type.in_(bean_type))
    if roast_level:
        stmt = stmt.where(Product.roast_level.in_(roast_level))
    if grind:
        stmt = stmt.where(Product.grind.in_(grind))
    if flavour:
        stmt = stmt.where(Product.flavour.in_(flavour))
    return stmt


@router.get("", response_model=ProductListOut)
async def list_products(
    db: DbSession,
    bean_type: Annotated[list[BeanType] | None, Query()] = None,
    roast_level: Annotated[list[RoastLevel] | None, Query()] = None,
    grind: Annotated[list[Grind] | None, Query()] = None,
    flavour: Annotated[list[Flavour] | None, Query()] = None,
    bestseller: bool | None = None,
    sort: SortOption = "featured",
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=60)] = 12,
) -> ProductListOut:
    base = select(Product).where(Product.is_active.is_(True))
    base = _apply_filters(base, bean_type, roast_level, grind, flavour)
    if bestseller is not None:
        base = base.where(Product.is_bestseller.is_(bestseller))

    count_stmt = select(func.count()).select_from(base.subquery())
    total = (await db.scalar(count_stmt)) or 0

    if sort in ("price_asc", "price_desc"):
        # Sort by the cheapest variant, which is the price shown on the card.
        min_price = (
            select(func.min(ProductVariant.price_paise))
            .where(ProductVariant.product_id == Product.id)
            .scalar_subquery()
        )
        base = base.order_by(min_price.asc() if sort == "price_asc" else min_price.desc())
    elif sort == "newest":
        base = base.order_by(Product.created_at.desc(), Product.id.desc())
    else:
        base = base.order_by(Product.is_bestseller.desc(), Product.id.asc())

    stmt = base.offset((page - 1) * page_size).limit(page_size)
    products = (await db.scalars(stmt)).unique().all()

    total_pages = (total + page_size - 1) // page_size if total else 0
    return ProductListOut(
        items=[ProductOut.model_validate(p) for p in products],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/facets", response_model=FacetsOut)
async def product_facets(db: DbSession) -> FacetsOut:
    """Counts per filter value across the active catalog.

    Declared before /{slug} so 'facets' is not swallowed by the slug route.
    """
    facets: dict[str, list[FacetValue]] = {}

    for field in ("bean_type", "roast_level", "grind", "flavour"):
        column = getattr(Product, field)
        stmt = (
            select(column, func.count(Product.id))
            .where(Product.is_active.is_(True))
            .group_by(column)
        )
        rows = (await db.execute(stmt)).all()
        labels = LABELS[field]
        facets[field] = sorted(
            (
                FacetValue(
                    value=str(value),
                    label=labels.get(str(value), str(value).replace("_", " ").title()),
                    count=count,
                )
                for value, count in rows
            ),
            key=lambda f: -f.count,
        )

    return FacetsOut(**facets)


@router.get("/{slug}", response_model=ProductOut)
async def get_product(slug: str, db: DbSession) -> ProductOut:
    product = await db.scalar(
        select(Product).where(Product.slug == slug, Product.is_active.is_(True))
    )
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return ProductOut.model_validate(product)
