# from sqlalchemy.orm import Session
#
# import models
# import schemas
#
#
# def get_all_items(db: Session):
#     return db.query(models.TodoItem).all()
#
#
# def get_item(db: Session, item_id: int):
#     return db.query(models.TodoItem).filter(models.TodoItem.id == item_id).first()
#
#
# def delete_item(db: Session, item_id: int):
#     item = get_item(db, item_id)
#     item.delete()
#     db.commit()
#
#
# def create_item(db: Session, item: schemas.TodoItemCreate) -> schemas.TodoItem:
#     new_item = models.TodoItem(**item.dict())
#     db.add(new_item)
#     db.commit()
#     db.refresh(new_item)
#     return new_item
#
#
# def update_item(db: Session, item: schemas.TodoItem) -> schemas.TodoItem:
#     db.query(models.TodoItem).filter(models.TodoItem.id == item.id).update(item.dict(exclude={"id"}))
#     db.commit()
#     return get_item(db=db, item_id=item.id)
#
