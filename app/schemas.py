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
    DEBIT = "DEBIT"
    CREDIT = "CREDIT"


class WalletEvent(Event):
    type: EventType


class WalletCreateEvent(WalletEvent):
    title: str
    type = EventType.CREATED


class WalletUpdateEvent(WalletEvent):
    title: str
    type = EventType.UPDATED


class WalletTransactionEvent(WalletEvent):
    amount: float


class WalletDebitEvent(WalletTransactionEvent):
    type = EventType.DEBIT


class WalletCreditEvent(WalletTransactionEvent):
    type = EventType.CREDIT


class WalletEventBase(BaseModel):
    title: str


class WalletCreatedEventIn(WalletEventBase):
    pass


class WalletDebitEventIn(BaseModel):
    amount: float = 0.0


class WalletCreditEventIn(BaseModel):
    amount: float = 0.0


class Wallet(WalletEventBase):
    entity_id: str
    amount: float = 0.0

    class Config:
        orm_mode = True
