from pydantic import BaseModel, EmailStr, Field, field_validator


class ContactMessageIn(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    email: EmailStr
    phone: str = Field(default="", max_length=20)
    subject: str = Field(default="general", max_length=120)
    message: str = Field(min_length=10, max_length=4000)

    @field_validator("phone")
    @classmethod
    def phone_is_blank_or_plausible(cls, v: str) -> str:
        """Optional — but if given, it should be a real Indian mobile number."""
        v = v.strip()
        if not v:
            return ""
        digits = v.removeprefix("+91").replace(" ", "").replace("-", "")
        if not digits.isdigit() or len(digits) != 10:
            raise ValueError("Enter a 10-digit mobile number, or leave it blank")
        return digits

    @field_validator("name", "message")
    @classmethod
    def not_only_whitespace(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("This field cannot be blank")
        return v.strip()


class ContactMessageOut(BaseModel):
    """Deliberately minimal — the browser has no business reading the queue."""

    ok: bool = True
    reference: str
