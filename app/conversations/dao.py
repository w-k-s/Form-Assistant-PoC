from datetime import datetime, timezone

from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncConnection

from app.conversations.models import (
    MessageId,
    ThreadId,
    generate_message_id,
    generate_thread_id,
    messages,
    threads,
)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


async def create_thread(
    conn: AsyncConnection,
    user_id: str | None = None,
) -> dict:
    thread_id: ThreadId = generate_thread_id()
    await conn.execute(
        insert(threads).values(
            id=thread_id,
            user_id=user_id,
            title="New chat",
            created_at=_utcnow(),
        )
    )
    await conn.commit()
    result = await conn.execute(select(threads).where(threads.c.id == thread_id))
    return dict(result.mappings().one())


async def get_thread(
    conn: AsyncConnection,
    thread_id: ThreadId,
) -> dict | None:
    result = await conn.execute(select(threads).where(threads.c.id == thread_id))
    thread_row = result.mappings().one_or_none()
    if thread_row is None:
        return None

    msgs_result = await conn.execute(
        select(messages)
        .where(messages.c.thread_id == thread_id)
        .order_by(messages.c.created_at)
    )
    return {
        **dict(thread_row),
        "messages": [dict(r) for r in msgs_result.mappings()],
    }


async def list_threads(
    conn: AsyncConnection,
    user_id: str | None,
) -> list[dict]:
    stmt = select(threads).order_by(threads.c.created_at.desc())
    if user_id:
        stmt = stmt.where(threads.c.user_id == user_id)
    else:
        stmt = stmt.where(threads.c.user_id.is_(None))
    result = await conn.execute(stmt)
    return [dict(r) for r in result.mappings()]


async def delete_thread(
    conn: AsyncConnection,
    thread_id: ThreadId,
) -> bool:
    result = await conn.execute(delete(threads).where(threads.c.id == thread_id))
    await conn.commit()
    return result.rowcount > 0


async def delete_threads(
    conn: AsyncConnection,
    thread_ids: list[ThreadId],
) -> int:
    if not thread_ids:
        return 0
    result = await conn.execute(delete(threads).where(threads.c.id.in_(thread_ids)))
    await conn.commit()
    return result.rowcount


async def delete_all_threads(
    conn: AsyncConnection,
    user_id: str | None,
) -> int:
    stmt = delete(threads)
    if user_id:
        stmt = stmt.where(threads.c.user_id == user_id)
    else:
        stmt = stmt.where(threads.c.user_id.is_(None))
    result = await conn.execute(stmt)
    await conn.commit()
    return result.rowcount


async def add_message(
    conn: AsyncConnection,
    thread_id: ThreadId,
    role: str,
    content: str,
) -> dict:
    msg_id: MessageId = generate_message_id()
    now = _utcnow()
    await conn.execute(
        insert(messages).values(
            id=msg_id,
            thread_id=thread_id,
            role=role,
            content=content,
            created_at=now,
        )
    )
    if role == "user":
        title = content[:60] + ("..." if len(content) > 60 else "")
        await conn.execute(
            update(threads)
            .where(threads.c.id == thread_id)
            .where(threads.c.title == "New chat")
            .values(title=title)
        )
    await conn.commit()
    result = await conn.execute(select(messages).where(messages.c.id == msg_id))
    return dict(result.mappings().one())
