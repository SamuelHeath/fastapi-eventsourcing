import json

from sqlalchemy.orm import Session

import models
import schemas
from repository import TodoItemReadRepository, TodoItemWriteRepository


class TodoItemDomainModel:

    def __init__(self, db: Session, item_id=None):
        self._id = item_id
        self._title = None
        self._read_repository = TodoItemReadRepository(db=db)
        self._write_repository = TodoItemWriteRepository(db=db)

    def load_state(self, item_id: str = None):
        if item_id is None and self._id is None:
            raise Exception("Missing id")
        else:
            item_id = self._id if item_id is None else item_id
            events = self._read_repository.get_events(item_id)
            for event in events:
                self.apply(event)

    def apply(self, event: models.TodoItemEvent):
        result = json.loads(event.data)
        if result["type"] == schemas.EventType.CREATED:
            self._apply(schemas.TodoItemCreatedEvent(**result))
        elif result["type"] == schemas.EventType.UPDATED:
            self._apply(schemas.TodoItemUpdatedEvent(**result))

    def _apply(self, event: schemas.TodoItemEvent, item_id=None):
        if item_id is not None:
            self._id = item_id
        if isinstance(event, schemas.TodoItemCreatedEvent) or isinstance(event, schemas.TodoItemUpdatedEvent):
            self._title = event.title

    def handle(self, event: schemas.TodoItemEvent):
        item = None
        if isinstance(event, schemas.TodoItemCreatedEvent):
            item = self._write_repository.create_todo_item(event=event)
        elif isinstance(event, schemas.TodoItemUpdatedEvent):
            item = self._write_repository.update_todo_item(item_id=self._id, event=event)

        if item is not None:
            self._apply(event, item.entity_id)

    def get_schema(self):
        return schemas.TodoItem(title=self._title, id=self._id)
