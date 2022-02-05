import uuid

from sqlalchemy.orm import Session

import models
import schemas


class TodoItemReadRepository:

    def __init__(self, db: Session):
        # This db session should really be an adapter allowing any persistence backend
        self._db = db

    def get_events(self, item_id: str):
        return self._db.query(models.TodoItemEvent).filter(models.TodoItemEvent.entity_id == item_id).all()


class TodoItemWriteRepository:
    def __init__(self, db: Session):
        self._db = db

    def _append_event(self, event: schemas.TodoItemEvent):
        item = models.TodoItemEvent(uuid=event.uuid, data=event.json(exclude={'uuid'}))
        self._db.add(item)
        self._db.commit()
        self._db.refresh(item)
        return item

    def create_todo_item(self, event: schemas.TodoItemCreatedEvent):
        item = self._append_event(event)
        item.entity_id = str(uuid.uuid4())
        self._db.commit()
        self._db.refresh(item)
        return item

    def update_todo_item(self, item_id: str, event: schemas.TodoItemUpdatedEvent):
        item = models.TodoItemEvent(uuid=event.uuid, entity_id=item_id, data=event.json(exclude={'uuid'}))
        self._db.add(item)
        self._db.commit()
        self._db.refresh(item)
        return item
