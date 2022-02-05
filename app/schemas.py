import datetime
import enum
import uuid

from pydantic import BaseModel, Field


def _generate_uuid():
    return str(uuid.uuid4())


class Event(BaseModel):
    uuid: str = Field(default_factory=_generate_uuid)
    created: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


class EventType(str, enum.Enum):
    CREATED = "CREATED"
    UPDATED = "UPDATED"


class TodoItemEvent(Event):
    title: str
    type: EventType


class TodoItemCreatedEvent(TodoItemEvent):
    type: str = EventType.CREATED


class TodoItemUpdatedEvent(TodoItemEvent):
    type: str = EventType.UPDATED


class TodoItemBase(BaseModel):
    title: str


class TodoItemCreate(TodoItemBase):
    pass


class TodoItem(TodoItemBase):
    id: str

    class Config:
        orm_mode = True
