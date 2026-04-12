from typing import NewType

import sqlalchemy as sa

from app.db.metadata import metadata
from app.sequencer import generate

ThreadId = NewType("ThreadId", str)
MessageId = NewType("MessageId", str)


def generate_thread_id() -> ThreadId:
    return ThreadId("t_" + generate())


def generate_message_id() -> MessageId:
    return MessageId("msg_" + generate())


threads = sa.Table(
    "threads",
    metadata,
    sa.Column("id", sa.String(32), primary_key=True),
    sa.Column(
        "user_id",
        sa.String(32),
        sa.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    ),
    sa.Column("title", sa.String(256), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
)

messages = sa.Table(
    "messages",
    metadata,
    sa.Column("id", sa.String(32), primary_key=True),
    sa.Column(
        "thread_id",
        sa.String(32),
        sa.ForeignKey("threads.id", ondelete="CASCADE"),
        nullable=False,
    ),
    sa.Column("role", sa.String(32), nullable=False),
    sa.Column("content", sa.Text, nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
)
