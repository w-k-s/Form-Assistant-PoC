from datetime import datetime, timezone
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncConnection
from app.payments.models import NewPayment, PaymentId, generate_payment_id, payments


async def save_payment(conn: AsyncConnection, payment: NewPayment) -> NewPayment:
    await conn.execute(
        insert(payments).values(
            id=payment.id,
            user_id=payment.user_id,
            thread_id=payment.thread_id,
            checkout_session_id=payment.checkout_session_id,
            checkout_session_url=payment.checkout_session_url,
            amount_minor_units=payment.amount_minor_units,
            currency=payment.currency,
            status=payment.status,
            status_details=payment.status_details,
            created_at=datetime.now(timezone.utc),
        )
    )
    await conn.commit()
    return payment


async def get_payment_by_thread_id(conn: AsyncConnection, thread_id: str) -> NewPayment | None:
    row = (
        await conn.execute(
            select(payments)
            .where(payments.c.thread_id == thread_id)
            .order_by(payments.c.created_at.desc())
            .limit(1)
        )
    ).mappings().first()
    if row is None:
        return None
    return NewPayment(
        id=PaymentId(row["id"]),
        user_id=row["user_id"],
        thread_id=row["thread_id"],
        amount_minor_units=row["amount_minor_units"],
        currency=row["currency"],
        checkout_session_id=row["checkout_session_id"],
        checkout_session_url=row["checkout_session_url"],
        status=row["status"],
        status_details=row["status_details"],
    )


async def update_payment_status(
    conn: AsyncConnection,
    payment_id: PaymentId,
    status: str,
    status_details: str | None = None,
) -> PaymentId:
    await conn.execute(
        update(payments)
        .where(payments.c.id == payment_id)
        .values(status=status, status_details=status_details)
    )
    await conn.commit()
    return payment_id
