from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    environment: str = "development"

    database_url: str = "postgresql+asyncpg://manero:manero@localhost:5432/manero"
    sync_database_url: str = "postgresql+psycopg://manero:manero@localhost:5432/manero"

    # Comma-separated in .env, split into a list below.
    cors_origins: str = "http://localhost:5173"

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


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
