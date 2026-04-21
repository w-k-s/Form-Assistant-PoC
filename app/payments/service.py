from dataclasses import dataclass

import app.integrations as integrations
import app.payments.dao as dao
from app.users import UserId
from app.conversations import ThreadId
from app.payments.models import NewPayment, generate_payment_id
from app.db.session import engine


@dataclass
class CheckoutSessionResult:
    url: str
    status: str


async def get_or_create_checkout_session(
    user_id: UserId,
    thread_id: ThreadId,
    amount_minor_units: int,
    currency: str,
    success_url: str,
    cancel_url: str,
) -> CheckoutSessionResult:
    async with engine.connect() as conn:
        existing = await dao.get_payment_by_thread_id(conn, thread_id)
        if existing is not None and existing.checkout_session_url is not None:
            return CheckoutSessionResult(url=existing.checkout_session_url, status=existing.status)

        result = integrations.create_checkout_session(
            amount_minor_units=amount_minor_units,
            currency=currency,
            success_url=success_url,
            cancel_url=cancel_url,
        )

        payment = NewPayment(
            id=generate_payment_id(),
            user_id=user_id,
            thread_id=thread_id,
            amount_minor_units=amount_minor_units,
            currency=currency,
            checkout_session_id=result.session_id,
            checkout_session_url=result.url,
        )
        await dao.save_payment(conn, payment)
        await conn.commit()

    return CheckoutSessionResult(url=result.url, status="pending")
