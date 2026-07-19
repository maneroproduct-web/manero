"""Payment providers.

The store talks to a `PaymentProvider`, never to a gateway directly. Swapping
gateways is a config change (`PAYMENT_PROVIDER` in .env), not a code change.

Two providers ship today:

  dummy     — no account, no keys, no network. Simulates the whole handshake
              locally so the full checkout flow is exercisable in development.
  razorpay  — the real thing. Needs RAZORPAY_KEY_ID / RAZORPAY_KEY_SECRET.

Both implement the same signature handshake, so the verification path in
`api/v1/checkout.py` is identical whichever is active. Nothing about the
checkout flow changes when you switch — which is the point.
"""

import hashlib
import hmac
import secrets
from typing import Protocol

from app.core.config import settings


class PaymentError(RuntimeError):
    """Raised when a provider cannot be used or a gateway call fails."""


class PaymentProvider(Protocol):
    name: str

    def public_key(self) -> str:
        """Key the browser is allowed to see. Never the secret."""
        ...

    def create_order(self, amount_paise: int, receipt: str) -> str:
        """Create the order at the gateway and return its id."""
        ...

    def verify(self, order_id: str, payment_id: str, signature: str) -> bool:
        """Confirm the gateway really authorised this payment."""
        ...


def _sign(secret: str, order_id: str, payment_id: str) -> str:
    """HMAC-SHA256 of '<order_id>|<payment_id>'. Razorpay's scheme."""
    return hmac.new(
        secret.encode(), f"{order_id}|{payment_id}".encode(), hashlib.sha256
    ).hexdigest()


class DummyProvider:
    """A fake gateway for development.

    Signs with a local secret using the same HMAC scheme as the real thing, so
    `verify` is genuinely exercised rather than stubbed out. The secret still
    never reaches the browser: the frontend asks the server to simulate the
    gateway callback (see POST /checkout/dummy-pay) and gets back a signed
    payload, exactly as a real gateway would hand one over.

    Never selectable when ENVIRONMENT=production — see `get_provider`.
    """

    name = "dummy"

    def public_key(self) -> str:
        return "dummy_key"

    def create_order(self, amount_paise: int, receipt: str) -> str:
        return f"dummy_order_{secrets.token_hex(8)}"

    def sign(self, order_id: str, payment_id: str) -> str:
        return _sign(settings.dummy_payment_secret, order_id, payment_id)

    def verify(self, order_id: str, payment_id: str, signature: str) -> bool:
        return hmac.compare_digest(self.sign(order_id, payment_id), signature)


class RazorpayProvider:
    name = "razorpay"

    def __init__(self) -> None:
        if not (settings.razorpay_key_id and settings.razorpay_key_secret):
            raise PaymentError(
                "PAYMENT_PROVIDER=razorpay but the keys are missing. Set "
                "RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET in backend/.env"
            )

    def public_key(self) -> str:
        return settings.razorpay_key_id

    def _client(self):
        import razorpay  # imported lazily so the dummy path needs no SDK

        return razorpay.Client(
            auth=(settings.razorpay_key_id, settings.razorpay_key_secret)
        )

    def create_order(self, amount_paise: int, receipt: str) -> str:
        try:
            order = self._client().order.create(
                {
                    "amount": amount_paise,
                    "currency": "INR",
                    "receipt": receipt,
                    "payment_capture": 1,
                }
            )
        except Exception as exc:
            raise PaymentError(f"Could not create Razorpay order: {exc}") from exc
        return order["id"]

    def verify(self, order_id: str, payment_id: str, signature: str) -> bool:
        # compare_digest so a wrong signature can't be found byte-by-byte
        # through response timing.
        expected = _sign(settings.razorpay_key_secret, order_id, payment_id)
        return hmac.compare_digest(expected, signature)


_PROVIDERS: dict[str, type] = {
    "dummy": DummyProvider,
    "razorpay": RazorpayProvider,
}


def get_provider() -> PaymentProvider:
    name = settings.payment_provider.lower().strip()

    if name not in _PROVIDERS:
        raise PaymentError(
            f"Unknown PAYMENT_PROVIDER '{name}'. "
            f"Expected one of: {', '.join(sorted(_PROVIDERS))}"
        )

    # A fake gateway in production would accept forged payments as real ones.
    if name == "dummy" and settings.environment.lower() == "production":
        raise PaymentError(
            "The dummy payment provider is refused when ENVIRONMENT=production. "
            "Set PAYMENT_PROVIDER=razorpay and configure real keys."
        )

    return _PROVIDERS[name]()
