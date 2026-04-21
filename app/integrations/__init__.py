"""
Payment gateway integration contracts.

This module is the *only* entry point the rest of the application should use
when interacting with a payment gateway. The concrete gateway (e.g. Stripe) is
an implementation detail hidden behind the PaymentGateway protocol. To swap
gateways, replace the _gateway instance — no other code should need to change.
"""

from typing import Protocol

from app.integrations._types import CheckoutResult, PaymentStatus, PaymentStatusResult, FINAL_PAYMENT_STATUSES
from app.integrations.stripe import StripeGateway

__all__ = [
    "CheckoutResult",
    "PaymentStatus",
    "PaymentStatusResult",
    "FINAL_PAYMENT_STATUSES",
    "create_checkout_session",
    "check_payment_status",
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
