import stripe

from app.config import settings
from app.integrations._types import CheckoutResult, PaymentGatewayError, PaymentStatus, PaymentStatusResult

stripe.api_key = settings.stripe_restricted_api_key

_STRIPE_STATUS_MAP: dict[str, PaymentStatus] = {
    "complete": PaymentStatus.PAID,
    "expired": PaymentStatus.EXPIRED,
    "open": PaymentStatus.PENDING,
}


class StripeGateway:
    def create_checkout_session(
        self,
        amount_minor_units: int,
        currency: str,
        success_url: str,
        cancel_url: str,
    ) -> CheckoutResult:
        try:
            session = stripe.checkout.Session.create(
                mode="payment",
                line_items=[
                    {
                        "price_data": {
                            "currency": currency,
                            "unit_amount": amount_minor_units,
                            "product_data": {"name": "Insurance Premium"},
                        },
                        "quantity": 1,
                    }
                ],
                success_url=success_url,
                cancel_url=cancel_url,
            )
        except stripe.StripeError as e:
            raise PaymentGatewayError(str(e)) from e
        return CheckoutResult(session_id=session.id, url=session.url)

    def check_payment_status(self, session_id: str) -> PaymentStatusResult:
        try:
            session = stripe.checkout.Session.retrieve(session_id)
        except stripe.StripeError as e:
            raise PaymentGatewayError(str(e)) from e
        status = _STRIPE_STATUS_MAP.get(session.status, PaymentStatus.FAILED)
        return PaymentStatusResult(status=status)
