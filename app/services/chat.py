import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.conversation import Message, Thread


async def create_thread(db: AsyncSession, user_id: uuid.UUID | None = None) -> Thread:
    thread = Thread(user_id=user_id)
    db.add(thread)
    await db.commit()
    await db.refresh(thread)
    return thread


async def get_thread(db: AsyncSession, thread_id: uuid.UUID) -> Thread | None:
    result = await db.execute(
        select(Thread)
        .where(Thread.id == thread_id)
        .options(selectinload(Thread.messages))
    )
    return result.scalar_one_or_none()


async def list_threads(db: AsyncSession, user_id: uuid.UUID | None) -> list[Thread]:
    stmt = select(Thread).order_by(Thread.created_at.desc())
    if user_id:
        stmt = stmt.where(Thread.user_id == user_id)
    else:
        stmt = stmt.where(Thread.user_id.is_(None))
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def delete_thread(db: AsyncSession, thread_id: uuid.UUID) -> bool:
    thread = await db.get(Thread, thread_id)
    if not thread:
        return False
    await db.delete(thread)
    await db.commit()
    return True


async def delete_threads(db: AsyncSession, thread_ids: list[uuid.UUID]) -> int:
    count = 0
    for tid in thread_ids:
        thread = await db.get(Thread, tid)
        if thread:
            await db.delete(thread)
            count += 1
    await db.commit()
    return count


async def delete_all_threads(db: AsyncSession, user_id: uuid.UUID | None) -> int:
    stmt = select(Thread)
    if user_id:
        stmt = stmt.where(Thread.user_id == user_id)
    else:
        stmt = stmt.where(Thread.user_id.is_(None))
    result = await db.execute(stmt)
    threads = list(result.scalars().all())
    for thread in threads:
        await db.delete(thread)
    await db.commit()
    return len(threads)


async def add_message(
    db: AsyncSession,
    thread_id: uuid.UUID,
    role: str,
    content: str,
) -> Message:
    message = Message(thread_id=thread_id, role=role, content=content)
    db.add(message)

    # Update thread title from first user message
    if role == "user":
        thread = await db.get(Thread, thread_id)
        if thread and thread.title == "New chat":
            thread.title = content[:60] + ("..." if len(content) > 60 else "")

    await db.commit()
    await db.refresh(message)
    return message
