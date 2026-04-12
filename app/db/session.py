from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

from app.config import settings

engine = create_async_engine(settings.database_url, echo=False)


async def get_conn() -> AsyncGenerator[AsyncConnection, None]:
    async with engine.connect() as conn:
        yield conn
