from dataclasses import dataclass
from typing import NewType

import sqlalchemy as sa

from app.db.metadata import metadata
from app.sequencer import generate

PaymentId = NewType("PaymentId", str)


def generate_payment_id() -> PaymentId:
    return PaymentId("pay_" + generate())


@dataclass
class NewPayment:
    """Data required to create a new Payment record."""

    id: PaymentId

    amount_minor_units: int
    """Total charge in the smallest currency unit (e.g. 280000 for AED 2,800)."""

    currency: str
    """ISO 4217 currency code, lowercase (e.g. "aed")."""

    user_id: str | None = None
    """ID of the user who initiated the payment; None for anonymous sessions."""

    thread_id: str | None = None
    """ID of the conversation thread in which the payment was initiated."""

    checkout_session_id: str | None = None
    """Gateway-issued session identifier. Populated after the session is created."""

    checkout_session_url: str | None = None
    """Hosted checkout URL. Returned to the user so they can complete payment."""

    status: str = "pending"
    """Payment status: pending | paid | failed | expired | cancelled."""

    status_details: str | None = None
    """Free-text detail for non-successful statuses (e.g. a gateway decline code)."""


payments = sa.Table(
    "payments",
    metadata,
    sa.Column("id", sa.String(32), primary_key=True),
    sa.Column(
        "user_id",
        sa.String(32),
        sa.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    ),
    sa.Column(
        "thread_id",
        sa.String(32),
        sa.ForeignKey("threads.id", ondelete="SET NULL"),
        nullable=True,
    ),
    sa.Column("checkout_session_id", sa.String(128), nullable=True),
    sa.Column("checkout_session_url", sa.Text, nullable=True),
    sa.Column(
        "amount_minor_units", sa.Integer, nullable=False
    ),  # e.g. 280000 for AED 2,800
    sa.Column("currency", sa.String(8), nullable=False),  # e.g. "aed"
    sa.Column(
        "status", sa.String(16), nullable=False
    ),  # pending | paid | failed | expired | cancelled
    sa.Column("status_details", sa.Text, nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
)
