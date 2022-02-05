from fastapi import FastAPI
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette import status

import domain
import models
from crud import get_all_items
from database import SessionLocal, engine
from schemas import TodoItem, TodoItemCreate, TodoItemCreatedEvent, TodoItemUpdatedEvent

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", status_code=status.HTTP_200_OK, response_model=list[TodoItem])
def get_todo_list(db: Session = Depends(get_db)):
    return get_all_items(db=db)


@app.get("/test/{todo_uuid}")
def handle_id(todo_uuid: str, db: Session = Depends(get_db)):
    model = domain.TodoItemDomainModel(db=db, item_id=todo_uuid)
    model.load_state(todo_uuid)
    return model.get_schema()


@app.put("/test/{todo_uuid}")
def handle_update(todo_uuid: str, item: TodoItem, db: Session = Depends(get_db)):
    model = domain.TodoItemDomainModel(db=db, item_id=item.id)
    model.load_state(todo_uuid)
    model.handle(TodoItemUpdatedEvent(title=item.title))
    return model.get_schema()


@app.post("/test/")
def handle_create(item: TodoItemCreate, db: Session = Depends(get_db)):
    model = domain.TodoItemDomainModel(db=db)
    model.handle(TodoItemCreatedEvent(title=item.title))
    return model.get_schema()
