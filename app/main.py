import os
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from starlette.middleware.sessions import SessionMiddleware

from app.agent.graph import build_graph
from app.api import auth, chat, deadlines, pages, rag
from app.config import settings
from app.db.qdrant import create_qdrant_client, ensure_collection
from app.db.session import engine
from app.logging import setup_logging

setup_logging()

logger = structlog.get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Build LangGraph graph with async PostgreSQL checkpointer
    # Use a sync-compatible connection string (psycopg3)
    pg_conn_str = settings.database_url.replace(
        "postgresql+asyncpg://", "postgresql://"
    )
    qdrant_client = await create_qdrant_client()
    await ensure_collection(qdrant_client)
    app.state.qdrant_client = qdrant_client

    async with AsyncPostgresSaver.from_conn_string(pg_conn_str) as checkpointer:
        await checkpointer.setup()
        graph = build_graph(checkpointer=checkpointer)
        app.state.graph = graph
        app.state.checkpointer = checkpointer
        logger.info("app started")

        yield

    await qdrant_client.close()
    await engine.dispose()


app = FastAPI(title="AI Form", lifespan=lifespan)

app.add_middleware(SessionMiddleware, secret_key=settings.jwt_secret)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if os.path.isdir("frontend/dist/assets"):
    app.mount("/assets", StaticFiles(directory="frontend/dist/assets"), name="assets")

# pages.router contains the SPA catch-all — must be included last
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(deadlines.router)
app.include_router(rag.router)
app.include_router(pages.router)
