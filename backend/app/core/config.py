from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# A known, published value. Fine for local development; fatal in production,
# which is enforced below rather than left to a README anyone can skip.
DEV_JWT_SECRET = "dev-only-insecure-jwt-secret-change-me"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    environment: str = "development"

    database_url: str = "postgresql+asyncpg://manero:manero@localhost:5432/manero"
    sync_database_url: str = "postgresql+psycopg://manero:manero@localhost:5432/manero"

    # Comma-separated in .env, split into a list below.
    cors_origins: str = "http://localhost:5173"

    # --- Admin auth ---
    # Signs admin session tokens. Anyone who knows this can mint a valid admin
    # token, so it must be long, random, and different in every environment.
    # Generate one with:  python -c "import secrets; print(secrets.token_urlsafe(48))"
    jwt_secret: str = DEV_JWT_SECRET
    access_token_minutes: int = 720  # 12 hours

    # "dummy" (no keys, dev only) or "razorpay". See services/payments.py.
    payment_provider: str = "dummy"
    dummy_payment_secret: str = "dummy-local-signing-secret"

    razorpay_key_id: str = ""
    razorpay_key_secret: str = ""

    shipping_fee_paise: int = 4900
    free_shipping_threshold_paise: int = 59900

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def razorpay_configured(self) -> bool:
        return bool(self.razorpay_key_id and self.razorpay_key_secret)

    @property
    def using_dummy_payments(self) -> bool:
        return self.payment_provider.lower().strip() == "dummy"

    @model_validator(mode="after")
    def production_must_not_use_dev_secrets(self) -> "Settings":
        """Refuse to boot production with the shipped development secret.

        A hard failure at startup, not a warning in a log nobody reads: with the
        default secret, anyone reading this repository can forge an admin token.
        """
        if self.environment.lower().strip() == "production":
            if self.jwt_secret == DEV_JWT_SECRET or len(self.jwt_secret) < 32:
                raise ValueError(
                    "JWT_SECRET is unset, too short, or still the development "
                    "default while ENVIRONMENT=production. Generate one with:\n"
                    '  python -c "import secrets; print(secrets.token_urlsafe(48))"'
                )
        return self


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
