import uuid

from fastapi import APIRouter, Depends, HTTPException
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from app.db.session import get_db
from app.dependencies import get_current_user
from app.schemas.chat import MessageCreate, MessageOut, ThreadOut, ThreadWithMessages, ThreadsDelete
from app.services.chat import add_message, create_thread, delete_all_threads, delete_thread, delete_threads, get_thread, list_threads

router = APIRouter(prefix="/api")


# Injected by main.py lifespan
_graph = None
_checkpointer: AsyncPostgresSaver | None = None


def set_graph(graph, checkpointer):
    global _graph, _checkpointer
    _graph = graph
    _checkpointer = checkpointer


@router.post("/threads", response_model=ThreadOut, status_code=201)
async def create_new_thread(
    db: AsyncSession = Depends(get_db),
    current_user: dict | None = Depends(get_current_user),
):
    user_id = uuid.UUID(current_user["sub"]) if current_user else None
    thread = await create_thread(db, user_id)
    return thread


@router.get("/threads", response_model=list[ThreadOut])
async def get_threads(
    db: AsyncSession = Depends(get_db),
    current_user: dict | None = Depends(get_current_user),
):
    user_id = uuid.UUID(current_user["sub"]) if current_user else None
    return await list_threads(db, user_id)


@router.get("/threads/{thread_id}", response_model=ThreadWithMessages)
async def get_thread_detail(
    thread_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    thread = await get_thread(db, thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    return thread


@router.delete("/threads", status_code=204)
async def delete_threads_endpoint(
    body: ThreadsDelete,
    db: AsyncSession = Depends(get_db),
):
    await delete_threads(db, body.thread_ids)


@router.delete("/threads/all", status_code=204)
async def delete_all_threads_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: dict | None = Depends(get_current_user),
):
    user_id = uuid.UUID(current_user["sub"]) if current_user else None
    await delete_all_threads(db, user_id)


@router.post("/threads/{thread_id}/messages", response_model=MessageOut)
async def post_message(
    thread_id: uuid.UUID,
    body: MessageCreate,
    db: AsyncSession = Depends(get_db),
):
    thread = await get_thread(db, thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    user_msg = await add_message(db, thread_id, "user", body.content)
    return user_msg


@router.get("/threads/{thread_id}/stream")
async def stream_thread(
    thread_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict | None = Depends(get_current_user),
):
    if _graph is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    thread = await get_thread(db, thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    latest_user_msg = next(
        (m for m in reversed(thread.messages) if m.role == "user"), None
    )
    if not latest_user_msg:
        raise HTTPException(status_code=400, detail="No user message to respond to")

    async def event_generator():
        lg_config = {
            "configurable": {
                "thread_id": str(thread_id),
                "user": current_user,
            }
        }
        full_reply: list[str] = []
        try:
            async for event in _graph.astream_events(
                {"messages": [HumanMessage(content=latest_user_msg.content)]},
                config=lg_config,
                version="v2",
            ):
                kind = event.get("event")
                if kind == "on_chat_model_stream":
                    chunk = event["data"]["chunk"]
                    token = ""
                    if hasattr(chunk, "content"):
                        c = chunk.content
                        if isinstance(c, str):
                            token = c
                        elif isinstance(c, list):
                            token = "".join(
                                p.get("text", "") if isinstance(p, dict) else str(p)
                                for p in c
                            )
                    if token:
                        full_reply.append(token)
                        yield {"event": "token", "data": token}
        finally:
            complete = "".join(full_reply)
            if complete:
                await add_message(db, thread_id, "assistant", complete)
            yield {"event": "done", "data": ""}

    return EventSourceResponse(event_generator())
