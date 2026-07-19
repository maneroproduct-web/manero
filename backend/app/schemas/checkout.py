from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.enums import OrderStatus


class ShippingAddressIn(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    line1: str = Field(min_length=3, max_length=255)
    line2: str = Field(default="", max_length=255)
    city: str = Field(min_length=2, max_length=120)
    state: str = Field(min_length=2, max_length=120)
    pincode: str = Field(min_length=6, max_length=6)

    @field_validator("pincode")
    @classmethod
    def pincode_is_six_digits(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("Pincode must be 6 digits")
        return v


class CreateOrderIn(BaseModel):
    cart_token: str
    email: EmailStr
    phone: str = Field(min_length=10, max_length=13)
    shipping: ShippingAddressIn

    @field_validator("phone")
    @classmethod
    def phone_is_plausible(cls, v: str) -> str:
        digits = v.removeprefix("+91").strip()
        if not digits.isdigit() or len(digits) != 10:
            raise ValueError("Enter a 10-digit mobile number")
        return digits


class CreateOrderOut(BaseModel):
    order_number: str
    # "dummy" or "razorpay" — tells the frontend which payment UI to open.
    provider: str
    provider_order_id: str
    public_key: str
    amount_paise: int
    currency: str = "INR"


class VerifyPaymentIn(BaseModel):
    provider_order_id: str
    provider_payment_id: str
    signature: str


class DummyPayIn(BaseModel):
    """Ask the dummy gateway to simulate a payment outcome."""

    provider_order_id: str
    succeed: bool = True


class DummyPayOut(BaseModel):
    """Shaped like a real gateway callback, so /verify handles it unchanged."""

    provider_order_id: str
    provider_payment_id: str
    signature: str


class OrderItemOut(BaseModel):
    product_name: str
    product_slug: str
    size_grams: int
    quantity: int
    unit_price_paise: int
    line_total_paise: int


class OrderOut(BaseModel):
    order_number: str
    status: OrderStatus
    email: str
    subtotal_paise: int
    shipping_paise: int
    total_paise: int
    shipping_name: str
    shipping_line1: str
    shipping_line2: str
    shipping_city: str
    shipping_state: str
    shipping_pincode: str
    items: list[OrderItemOut]
