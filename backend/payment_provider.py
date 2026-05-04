"""Payment provider abstraction layer.

Add new providers by subclassing PaymentProvider and registering in get_provider().
"""

import hashlib
import hmac
import logging
from abc import ABC, abstractmethod
from typing import Optional

import httpx

from config import settings

logger = logging.getLogger("openmeets.payment")


class PaymentProvider(ABC):
    """Abstract payment provider."""

    @abstractmethod
    async def create_order(
        self, amount: int, currency: str, receipt: str, notes: Optional[dict] = None
    ) -> dict:
        """Create a payment order. Returns provider-specific response dict."""

    @abstractmethod
    def verify_signature(self, provider_order_id: str, payment_id: str, signature: str) -> bool:
        """Verify client-side payment callback signature."""

    @abstractmethod
    def verify_webhook(self, raw_body: bytes, signature_header: str) -> bool:
        """Verify webhook signature from the provider."""

    @property
    @abstractmethod
    def public_key(self) -> str | None:
        """Public key / key ID exposed to frontend."""


class RazorpayProvider(PaymentProvider):
    """Razorpay integration."""

    API_BASE = "https://api.razorpay.com/v1"

    def __init__(self):
        self._key_id = settings.razorpay_key_id
        self._key_secret = settings.razorpay_key_secret
        self._webhook_secret = settings.razorpay_webhook_secret
        self._client: Optional[httpx.AsyncClient] = None

    def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.API_BASE,
                auth=httpx.BasicAuth(self._key_id, self._key_secret),
            )
        return self._client

    @property
    def public_key(self) -> str | None:
        return self._key_id

    async def create_order(
        self, amount: int, currency: str, receipt: str, notes: Optional[dict] = None
    ) -> dict:
        payload: dict = {
            "amount": amount,
            "currency": currency,
            "receipt": receipt,
        }
        if notes:
            payload["notes"] = notes

        resp = await self._get_client().post("/orders", json=payload)
        resp.raise_for_status()
        return resp.json()

    def verify_signature(self, provider_order_id: str, payment_id: str, signature: str) -> bool:
        message = f"{provider_order_id}|{payment_id}"
        expected = hmac.new(
            self._key_secret.encode(),
            message.encode(),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    def verify_webhook(self, raw_body: bytes, signature_header: str) -> bool:
        if not self._webhook_secret:
            logger.warning("RAZORPAY_WEBHOOK_SECRET not configured")
            return False

        expected = hmac.new(
            self._webhook_secret.encode(),
            raw_body,
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature_header)


_providers: dict[str, PaymentProvider] = {}


def get_provider(name: str = "razorpay") -> PaymentProvider:
    if name not in _providers:
        match name:
            case "razorpay":
                _providers[name] = RazorpayProvider()
            case _:
                raise ValueError(f"Unknown payment provider: {name}")
    return _providers[name]
