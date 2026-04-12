from datetime import datetime

from pydantic import BaseModel


class MessageCreate(BaseModel):
    content: str


class ThreadsDelete(BaseModel):
    thread_ids: list[str]


class MessageOut(BaseModel):
    id: str
    thread_id: str
    role: str
    content: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ThreadOut(BaseModel):
    id: str
    title: str
    created_at: datetime

    model_config = {"from_attributes": True}


class ThreadWithMessages(BaseModel):
    id: str
    title: str
    created_at: datetime
    messages: list[MessageOut]

    model_config = {"from_attributes": True}
