"""
Payment gateway integration contracts.

This module is the *only* entry point the rest of the application should use
when interacting with a payment gateway. The concrete gateway (e.g. Stripe) is
an implementation detail hidden behind the PaymentGateway protocol. To swap
gateways, replace the _gateway instance — no other code should need to change.
"""

from typing import Protocol

from app.integrations._types import (
    CheckoutResult,
    PaymentGatewayError,
    PaymentStatus,
    PaymentStatusResult,
    FINAL_PAYMENT_STATUSES,
)
from app.integrations.stripe import StripeGateway
from app.integrations.s3 import S3Storage

__all__ = [
    "CheckoutResult",
    "PaymentGatewayError",
    "PaymentStatus",
    "PaymentStatusResult",
    "FINAL_PAYMENT_STATUSES",
    "create_checkout_session",
    "check_payment_status",
    "upload_file",
    "generate_presigned_url",
]


class PaymentGateway(Protocol):
    def create_checkout_session(
        self,
        amount_minor_units: int,
        currency: str,
        success_url: str,
        cancel_url: str,
    ) -> CheckoutResult: ...

    def check_payment_status(self, session_id: str) -> PaymentStatusResult: ...


_gateway: PaymentGateway = StripeGateway()


def create_checkout_session(
    amount_minor_units: int,
    currency: str,
    success_url: str,
    cancel_url: str,
) -> CheckoutResult:
    return _gateway.create_checkout_session(
        amount_minor_units, currency, success_url, cancel_url
    )


def check_payment_status(session_id: str) -> PaymentStatusResult:
    return _gateway.check_payment_status(session_id)


class ObjectStorage(Protocol):
    def upload(self, source_path: str, destination_bucket: str, key: str) -> None: ...

    def generate_presigned_url(
        self, destination_bucket: str, key: str, expires_in: int = 3600
    ) -> str: ...


_storage: ObjectStorage = S3Storage()


def upload_file(source_path: str, destination_bucket: str, key: str) -> None:
    _storage.upload(source_path, destination_bucket, key)


def generate_presigned_url(
    destination_bucket: str, key: str, expires_in: int = 3600
) -> str:
    return _storage.generate_presigned_url(destination_bucket, key, expires_in)
