import uuid
from datetime import datetime

from pydantic import BaseModel


class MessageCreate(BaseModel):
    content: str


class ThreadsDelete(BaseModel):
    thread_ids: list[uuid.UUID]


class MessageOut(BaseModel):
    id: uuid.UUID
    thread_id: uuid.UUID
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ThreadOut(BaseModel):
    id: uuid.UUID
    title: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ThreadWithMessages(BaseModel):
    id: uuid.UUID
    title: str
    created_at: datetime
    messages: list[MessageOut]

    model_config = {"from_attributes": True}
