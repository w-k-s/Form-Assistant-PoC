from datetime import datetime, timezone
from typing import NewType

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.sequencer import generate

UserId = NewType("UserId", str)


def generate_user_id(suffix: str | None = None) -> UserId:
    return UserId("u_" + (suffix if suffix is not None else generate()))


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[UserId] = mapped_column(
        String(32), primary_key=True, default=generate_user_id
    )
    google_id: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(256), nullable=False)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    picture: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow
    )

    threads: Mapped[list["Thread"]] = relationship(back_populates="user")
