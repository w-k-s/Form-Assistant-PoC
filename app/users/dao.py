from datetime import datetime, timezone

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncConnection

from app.users.models import User, generate_user_id


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


async def get_user_by_google_id(conn: AsyncConnection, google_id: str) -> dict | None:
    result = await conn.execute(select(User).where(User.c.google_id == google_id))
    row = result.mappings().one_or_none()
    return dict(row) if row else None


async def create_user(
    conn: AsyncConnection,
    google_id: str,
    email: str,
    name: str,
    picture: str | None,
) -> dict:
    user_id = generate_user_id()
    await conn.execute(
        insert(User).values(
            id=user_id,
            google_id=google_id,
            email=email,
            name=name,
            picture=picture,
            created_at=_utcnow(),
        )
    )
    result = await conn.execute(select(User).where(User.c.id == user_id))
    return dict(result.mappings().one())


async def update_user(
    conn: AsyncConnection,
    google_id: str,
    name: str,
    picture: str | None,
) -> None:
    await conn.execute(
        update(User)
        .where(User.c.google_id == google_id)
        .values(name=name, picture=picture)
    )
