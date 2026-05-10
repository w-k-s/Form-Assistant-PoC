from dataclasses import dataclass
from decimal import Decimal
import os

import structlog
import app.payments.dao as dao
from sqlalchemy.exc import SQLAlchemyError
from InvoiceGenerator.api import Invoice, Item, Client, Provider, Creator
from InvoiceGenerator.pdf import SimpleInvoice

from app.users import UserId
from app.conversations import ThreadId
from app.payments.models import NewPayment, generate_payment_id
from app.db.session import engine
from app.config import settings
from app.integrations import (
    PaymentStatus,
    PaymentGatewayError,
    PaymentStatusResult,
    check_payment_status,
    create_checkout_session,
    FINAL_PAYMENT_STATUSES,
    upload_file,
    generate_presigned_url,
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


async def update_payment_status(conn, payment: NewPayment) -> PaymentStatusResult:
    if payment.status in FINAL_PAYMENT_STATUSES:
        log.info(
            "payment status is final", payment_id=payment.id, status=payment.status
        )
        return PaymentStatusResult(
            status=payment.status, status_details=payment.status_details
        )

    try:
        result = check_payment_status(payment.checkout_session_id)
        log.info("Updating payment status", payment_id=payment.id, result=result)
        await dao.update_payment_status(
            conn,
            payment_id=payment.id,
            status=result.status,
            status_details=result.status_details,
        )
        return result
    except PaymentGatewayError as e:
        log.warn("Failed to fetch payment status", payment_id=payment.id, exc_info=e)
        return PaymentStatusResult(PaymentStatus.UNKNOWN)
    except SQLAlchemyError as e:
        log.warn("Failed to update payment status", payment_id=payment.id, exc_info=e)
        return PaymentStatusResult(PaymentStatus.UNKNOWN)


async def generate_receipt(payment: NewPayment) -> str:
    os.environ["INVOICE_LANG"] = "en"
    client = Client("Mr. Require Login")

    provider = Provider("AnyInsurance")
    creator = Creator("Steve Ballmer")

    invoice = Invoice(client, provider, creator)
    invoice.currency_locale = "en_US.UTF-8"
    invoice.add_item(
        Item(1, Decimal(payment.amount_minor_units / 100), description="Insurance")
    )

    os.makedirs(settings.tmp_invoices_dir, exist_ok=True)
    local_path = os.path.join(settings.tmp_invoices_dir, f"{payment.id}.pdf")

    pdf = SimpleInvoice(invoice)
    pdf.gen(local_path)

    s3_key = f"{payment.id}.pdf"
    upload_file(local_path, settings.s3_invoices_bucket, s3_key)
    return generate_presigned_url(settings.s3_invoices_bucket, s3_key)
