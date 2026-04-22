from dataclasses import dataclass

import structlog
import app.payments.dao as dao
from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from app.users import UserId
from app.conversations import ThreadId
from app.payments.models import NewPayment, generate_payment_id
from app.db.session import engine
from app.integrations import (
    PaymentStatus,
    PaymentGatewayError,
    PaymentStatusResult,
    check_payment_status,
    create_checkout_session,
    FINAL_PAYMENT_STATUSES,
)

log = structlog.get_logger(__name__)


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
            return CheckoutSessionResult(
                url=existing.checkout_session_url, status=existing.status
            )

        result = create_checkout_session(
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


async def update_payment_status(
    user_id: UserId, thread_id: ThreadId
) -> PaymentStatusResult:
    async with engine.connect() as conn:
        existing = await dao.get_payment_by_thread_id(conn, thread_id)
        if existing is None:
            log.info(
                "Can not update payment status. thread not found", thread_id=thread_id
            )
            # Probably need to throw a non-http exception here
            raise HTTPException(status_code=404, detail="Payment not found")

        if existing.status in FINAL_PAYMENT_STATUSES:
            log.info("payment status", thread_id=thread_id, result=result)
            return PaymentStatusResult(
                status=existing.status, status_details=existing.status_details
            )

        try:
            result = check_payment_status(existing.checkout_session_id)
            log.info("Updating payment status", thread_id=thread_id, result=result)
            await dao.update_payment_status(
                conn,
                payment_id=existing.id,
                status=result.status,
                status_details=result.status_details,
            )
            return result
        except PaymentGatewayError as e:
            log.warn("Failed to fetch payment status", thread_id=thread_id, exc_info=e)
            return PaymentStatusResult(PaymentStatus.UNKNOWN)
        except SQLAlchemyError as e:
            log.warn("Failed to update payment status", thread_id=thread_id, exc_info=e)
            return PaymentStatusResult(PaymentStatus.UNKNOWN)
