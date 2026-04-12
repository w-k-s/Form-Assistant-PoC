from typing import NewType

import sqlalchemy as sa

from app.db.metadata import metadata
from app.sequencer import generate

UserId = NewType("UserId", str)


def generate_user_id() -> UserId:
    return UserId("u_" + generate())


User = sa.Table(
    "users",
    metadata,
    sa.Column("id", sa.String(32), primary_key=True),
    sa.Column("google_id", sa.String(128), unique=True, nullable=False),
    sa.Column("email", sa.String(256), nullable=False),
    sa.Column("name", sa.String(256), nullable=False),
    sa.Column("picture", sa.Text, nullable=True),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
)
