import uuid

from sqlalchemy.orm import Session

from app import models
from app import schemas


class WalletEventReadRepository:
    def __init__(self, db: Session):
        # This db session should really be an adapter allowing any persistence backend
        self._db = db

    def get_events(self, item_id: str):
        return (
            self._db.query(models.WalletEvent)
                .filter(models.WalletEvent.entity_id == item_id)
                .all()
        )


class WalletEventWriteRepository:
    def __init__(self, db: Session):
        self._db = db

    def _append_event(self, event: schemas.WalletEvent):
        item = models.WalletEvent(uuid=event.uuid, data=event.json(exclude={"uuid"}))
        self._db.add(item)
        self._db.commit()
        self._db.refresh(item)
        return item

    def create_todo_item(self, event: schemas.WalletCreateEvent):
        item = self._append_event(event)
        item.entity_id = str(uuid.uuid4())
        self._db.commit()
        self._db.refresh(item)
        return item

    def update_todo_item(self, item_id: str, event: schemas.WalletUpdateEvent):
        item = models.WalletEvent(
            uuid=event.uuid, entity_id=item_id, data=event.json(exclude={"uuid"})
        )
        self._db.add(item)
        self._db.commit()
        self._db.refresh(item)
        return item

    def debit_amount(self, item_id: str, event: schemas.WalletDebitEvent):
        item = models.WalletEvent(
            uuid=event.uuid, entity_id=item_id, data=event.json(exclude={"uuid"})
        )
        self._db.add(item)
        self._db.commit()
        self._db.refresh(item)
        return item

    def credit_amount(self, item_id: str, event: schemas.WalletCreditEvent):
        item = models.WalletEvent(
            uuid=event.uuid, entity_id=item_id, data=event.json(exclude={"uuid"})
        )
        self._db.add(item)
        self._db.commit()
        self._db.refresh(item)
        return item
