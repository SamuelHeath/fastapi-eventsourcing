import json

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app import models
from app import schemas
from app.repository import WalletEventReadRepository, WalletEventWriteRepository


class WalletDomainModel:
    def __init__(self, db: Session, item_id=None):
        self._id = item_id
        self._sequence_id = 0
        self._title = None
        self._amount = 0.0
        self._read_repository = WalletEventReadRepository(db=db)
        self._write_repository = WalletEventWriteRepository(db=db)

    def load_state(self, item_id: str = None) -> None:
        if item_id is None and self._id is None:
            raise Exception("Missing id")
        else:
            item_id = self._id if item_id is None else item_id
            events = self._read_repository.get_events(item_id)
            if len(events) == 0:
                raise Exception("Entity does not exist!")

            for event in events:
                self.apply(event)

    def apply(self, event: models.WalletEvent):
        result = json.loads(event.data)
        _type = result["type"]
        if _type == schemas.EventType.CREATED:
            self._apply(schemas.WalletCreateEvent(**result))
        elif _type == schemas.EventType.UPDATED:
            self._apply(schemas.WalletUpdateEvent(**result))
        elif _type == schemas.EventType.DEBIT:
            self._apply(schemas.WalletDebitEvent(**result))
        elif _type == schemas.EventType.CREDIT:
            self._apply(schemas.WalletCreditEvent(**result))

        self._sequence_id = event.sequence_id

    def _apply(self, event: schemas.WalletEvent, item_id=None):
        if item_id is not None:
            self._id = item_id
        if isinstance(event, schemas.WalletCreateEvent) or isinstance(
                event, schemas.WalletUpdateEvent
        ):
            self._title = event.title
        elif isinstance(event, schemas.WalletDebitEvent):
            self._amount += event.amount
        elif isinstance(event, schemas.WalletCreditEvent):
            self._amount -= event.amount

    def handle(self, event: schemas.WalletEvent) -> schemas.Wallet:
        item = None
        if isinstance(event, schemas.WalletCreateEvent):
            item = self._write_repository.create_todo_item(event=event)
        elif isinstance(event, schemas.WalletUpdateEvent):
            item = self._write_repository.update_todo_item(
                item_id=self._id, sequence_id=self._sequence_id, event=event
            )
        elif isinstance(event, schemas.WalletDebitEvent):
            item = self._write_repository.debit_amount(
                item_id=self._id, sequence_id=self._sequence_id, event=event
            )
        elif isinstance(event, schemas.WalletCreditEvent):
            if self._amount - event.amount < 0.0:
                raise HTTPException(status_code=400, detail="Insufficient Funds")
            item = self._write_repository.credit_amount(
                item_id=self._id, sequence_id=self._sequence_id, event=event
            )

        if item is not None:
            self._apply(event, item.entity_id)

        return self.get_state()

    def get_state(self) -> schemas.Wallet:
        return schemas.Wallet(
            title=self._title, entity_id=self._id, amount=self._amount
        )
