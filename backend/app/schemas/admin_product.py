from pydantic import BaseModel, Field, field_validator

from app.models.enums import BeanType, Flavour, Grind, RoastLevel


class VariantIn(BaseModel):
    """A size/price option. `id` is set when editing an existing one."""

    id: int | None = None
    size_grams: int = Field(gt=0, le=10_000)
    sku: str = Field(min_length=1, max_length=64)
    # Money is integer paise everywhere. 44900 == ₹449.00
    price_paise: int = Field(gt=0, le=100_000_000)
    compare_at_price_paise: int | None = Field(default=None, gt=0, le=100_000_000)
    stock_qty: int = Field(default=0, ge=0, le=1_000_000)

    @field_validator("sku")
    @classmethod
    def normalise_sku(cls, v: str) -> str:
        return v.strip().upper()


class ProductIn(BaseModel):
    slug: str = Field(min_length=2, max_length=120)
    name: str = Field(min_length=2, max_length=200)
    description: str = Field(default="", max_length=5000)

    bean_type: BeanType
    roast_level: RoastLevel
    grind: Grind
    flavour: Flavour

    origin: str = Field(default="", max_length=120)
    tasting_notes: str = Field(default="", max_length=300)
    image_url: str = Field(default="", max_length=500)

    is_active: bool = True
    is_bestseller: bool = False

    variants: list[VariantIn] = Field(min_length=1)

    @field_validator("slug")
    @classmethod
    def slug_is_url_safe(cls, v: str) -> str:
        v = v.strip().lower()
        if not all(c.isalnum() or c == "-" for c in v):
            raise ValueError("Slug may contain only letters, numbers and hyphens")
        if v.startswith("-") or v.endswith("-"):
            raise ValueError("Slug cannot start or end with a hyphen")
        return v

    @field_validator("variants")
    @classmethod
    def sizes_are_unique(cls, v: list[VariantIn]) -> list[VariantIn]:
        sizes = [x.size_grams for x in v]
        if len(sizes) != len(set(sizes)):
            raise ValueError("Each size can only appear once")
        skus = [x.sku for x in v]
        if len(skus) != len(set(skus)):
            raise ValueError("Each SKU must be unique")
        return v


class ProductPatch(BaseModel):
    """Partial update. Anything omitted is left alone.

    `variants` is all-or-nothing: send the complete list to replace them, or
    omit it to leave them untouched. A partial variant list would silently
    delete the sizes you didn't mention.
    """

    name: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=5000)

    bean_type: BeanType | None = None
    roast_level: RoastLevel | None = None
    grind: Grind | None = None
    flavour: Flavour | None = None

    origin: str | None = Field(default=None, max_length=120)
    tasting_notes: str | None = Field(default=None, max_length=300)
    image_url: str | None = Field(default=None, max_length=500)

    is_active: bool | None = None
    is_bestseller: bool | None = None

    variants: list[VariantIn] | None = None
