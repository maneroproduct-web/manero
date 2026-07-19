from pydantic import BaseModel, ConfigDict, computed_field

from app.core.money import format_inr
from app.models.enums import BeanType, Flavour, Grind, RoastLevel


class VariantOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    sku: str
    size_grams: int
    price_paise: int
    compare_at_price_paise: int | None
    stock_qty: int

    @computed_field
    @property
    def in_stock(self) -> bool:
        return self.stock_qty > 0

    @computed_field
    @property
    def price_display(self) -> str:
        return format_inr(self.price_paise)

    @computed_field
    @property
    def discount_percent(self) -> int | None:
        """Rounded percent off, matching how the reference stores badge products."""
        if not self.compare_at_price_paise or self.compare_at_price_paise <= self.price_paise:
            return None
        off = self.compare_at_price_paise - self.price_paise
        return round(off * 100 / self.compare_at_price_paise)


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    slug: str
    name: str
    description: str
    bean_type: BeanType
    roast_level: RoastLevel
    grind: Grind
    flavour: Flavour
    origin: str
    tasting_notes: str
    image_url: str
    is_bestseller: bool
    variants: list[VariantOut]


class ProductListOut(BaseModel):
    items: list[ProductOut]
    total: int
    page: int
    page_size: int
    total_pages: int


class FacetValue(BaseModel):
    value: str
    label: str
    count: int


class FacetsOut(BaseModel):
    """Filter options with counts, so the sidebar renders from real data."""

    bean_type: list[FacetValue]
    roast_level: list[FacetValue]
    grind: list[FacetValue]
    flavour: list[FacetValue]
