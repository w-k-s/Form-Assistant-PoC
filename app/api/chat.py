import structlog
from fastapi import APIRouter, Depends, HTTPException, Request
from langchain_core.messages import HumanMessage
from sqlalchemy.ext.asyncio import AsyncConnection
from sse_starlette.sse import EventSourceResponse

from app.conversations.schemas import (
    MessageCreate,
    MessageOut,
    ThreadOut,
    ThreadWithMessages,
    ThreadsDelete,
)
from app.db.session import get_conn
from app.dependencies import get_current_user
from app.services.chat import (
    add_message,
    create_thread,
    delete_all_threads,
    delete_thread,
    delete_threads,
    get_thread,
    list_threads,
)

log = structlog.get_logger(__name__)

router = APIRouter(prefix="/api")


@router.post("/threads", response_model=ThreadOut, status_code=201)
async def create_new_thread(
    conn: AsyncConnection = Depends(get_conn),
    current_user: dict | None = Depends(get_current_user),
):
    user_id = current_user["sub"] if current_user else None
    thread = await create_thread(conn, user_id)
    return thread


@router.get("/threads", response_model=list[ThreadOut])
async def get_threads(
    conn: AsyncConnection = Depends(get_conn),
    current_user: dict | None = Depends(get_current_user),
):
    user_id = current_user["sub"] if current_user else None
    return await list_threads(conn, user_id)


@router.get("/threads/{thread_id}", response_model=ThreadWithMessages)
async def get_thread_detail(
    thread_id: str,
    conn: AsyncConnection = Depends(get_conn),
):
    thread = await get_thread(conn, thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")
    return thread


@router.delete("/threads", status_code=204)
async def delete_threads_endpoint(
    body: ThreadsDelete,
    conn: AsyncConnection = Depends(get_conn),
):
    await delete_threads(conn, body.thread_ids)


@router.delete("/threads/all", status_code=204)
async def delete_all_threads_endpoint(
    conn: AsyncConnection = Depends(get_conn),
    current_user: dict | None = Depends(get_current_user),
):
    user_id = current_user["sub"] if current_user else None
    await delete_all_threads(conn, user_id)


@router.post("/threads/{thread_id}/messages", response_model=MessageOut)
async def post_message(
    thread_id: str,
    body: MessageCreate,
    conn: AsyncConnection = Depends(get_conn),
):
    thread = await get_thread(conn, thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    user_msg = await add_message(conn, thread_id, "user", body.content)
    return user_msg


@router.get("/threads/{thread_id}/stream")
async def stream_thread(
    thread_id: str,
    request: Request,
    conn: AsyncConnection = Depends(get_conn),
    current_user: dict | None = Depends(get_current_user),
):
    graph = request.app.state.graph
    if graph is None:
        raise HTTPException(status_code=503, detail="Agent not initialized")

    thread = await get_thread(conn, thread_id)
    if not thread:
        raise HTTPException(status_code=404, detail="Thread not found")

    latest_user_msg = next(
        (m for m in reversed(thread["messages"]) if m["role"] == "user"), None
    )
    if not latest_user_msg:
        raise HTTPException(status_code=400, detail="No user message to respond to")

    async def event_generator():
        lg_config = {
            "configurable": {
                "thread_id": thread_id,
                "user": current_user,
            }
        }
        full_reply: list[str] = []
        try:
            async for event in graph.astream_events(
                {"messages": [HumanMessage(content=latest_user_msg["content"])]},
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

                elif kind == "on_chat_model_end" and not full_reply:
                    # Bedrock doesn't emit streaming events — fall back to full output
                    output = event["data"].get("output")
                    if output and hasattr(output, "content"):
                        c = output.content
                        if isinstance(c, str):
                            token = c
                        elif isinstance(c, list):
                            token = "".join(
                                p.get("text", "") if isinstance(p, dict) else str(p)
                                for p in c
                            )
                        else:
                            token = ""
                        if token:
                            full_reply.append(token)
                            yield {"event": "token", "data": token}
        except Exception as e:
            log.error("Agent Exception", exc_info=e)
        finally:
            complete = "".join(full_reply)
            if complete:
                await add_message(conn, thread_id, "assistant", complete)
            yield {"event": "done", "data": ""}

    return EventSourceResponse(event_generator())
