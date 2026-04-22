from dataclasses import dataclass
from enum import Enum


class PaymentGatewayError(Exception):
    pass


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    UNKNOWN = "unknown"


FINAL_PAYMENT_STATUSES: frozenset[PaymentStatus] = frozenset(
    {
        PaymentStatus.PAID,
        PaymentStatus.FAILED,
        PaymentStatus.EXPIRED,
        PaymentStatus.CANCELLED,
    }
)


@dataclass(frozen=True)
class CheckoutResult:
    session_id: str
    url: str


@dataclass(frozen=True)
class PaymentStatusResult:
    status: PaymentStatus
    status_details: str | None = None
