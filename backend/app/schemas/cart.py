from pydantic import BaseModel, Field


class CartItemIn(BaseModel):
    variant_id: int
    quantity: int = Field(default=1, ge=1, le=99)


class CartItemQuantityIn(BaseModel):
    quantity: int = Field(ge=0, le=99)  # 0 removes the line


class CartItemOut(BaseModel):
    id: int
    variant_id: int
    quantity: int
    size_grams: int
    sku: str
    unit_price_paise: int
    line_total_paise: int
    stock_qty: int
    product_name: str
    product_slug: str
    image_url: str


class CartOut(BaseModel):
    token: str
    items: list[CartItemOut]
    item_count: int
    subtotal_paise: int
    shipping_paise: int
    total_paise: int
    free_shipping_threshold_paise: int
