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


class WalletEvent(Event):
    title: str
    type: EventType


class WalletCreatedEvent(WalletEvent):
    type: str = EventType.CREATED


class WalletUpdatedEvent(WalletEvent):
    type: str = EventType.UPDATED


class WalletEventBase(BaseModel):
    title: str


class WalletEventCreate(WalletEventBase):
    pass


class Wallet(WalletEventBase):
    entity_id: str

    class Config:
        orm_mode = True
