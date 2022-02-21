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

    def create_todo_item(self, event: schemas.WalletCreateEvent):
        item = self._create_wallet_event(item_id=str(uuid.uuid4()), sequence_id=0, event=event)
        return self._save_wallet_event(item=item)

    def _create_wallet_event(self, item_id: str, sequence_id: int, event: schemas.WalletEvent):
        return models.WalletEvent(uuid=event.uuid, entity_id=item_id, sequence_id=sequence_id + 1, data=event.json(exclude={"uuid"}))

    def _save_wallet_event(self, item: models.WalletEvent):
        self._db.add(item)
        self._db.commit()
        self._db.refresh(item)
        return item

    def update_todo_item(self, item_id: str, sequence_id: int, event: schemas.WalletUpdateEvent):
        item = self._create_wallet_event(item_id=item_id, sequence_id=sequence_id, event=event)
        return self._save_wallet_event(item=item)

    def debit_amount(self, item_id: str, sequence_id: int, event: schemas.WalletDebitEvent):
        item = self._create_wallet_event(item_id=item_id, sequence_id=sequence_id, event=event)
        return self._save_wallet_event(item=item)

    def credit_amount(self, item_id: str, sequence_id: int, event: schemas.WalletCreditEvent):
        item = self._create_wallet_event(item_id=item_id, sequence_id=sequence_id, event=event)
        return self._save_wallet_event(item=item)
