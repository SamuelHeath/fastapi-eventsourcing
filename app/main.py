from fastapi import FastAPI
from fastapi.params import Depends
from sqlalchemy.orm import Session

from app import domain
from app import models
from app.database import SessionLocal, engine
from app.schemas import Wallet, WalletEventCreate, WalletCreatedEvent, WalletUpdatedEvent

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#
# @app.get("/", status_code=status.HTTP_200_OK, response_model=list[Wallet])
# def get_todo_list(db: Session = Depends(get_db)):
#     return get_all_items(db=db)


@app.post("/wallet", response_model=Wallet)
def handle_create(item: WalletEventCreate, db: Session = Depends(get_db)):
    model = domain.WalletDomainModel(db=db)
    model.handle(WalletCreatedEvent(title=item.title))
    return model.get_schema()


@app.get("/wallet/{todo_uuid}", response_model=Wallet)
def handle_id(todo_uuid: str, db: Session = Depends(get_db)):
    model = domain.WalletDomainModel(db=db, item_id=todo_uuid)
    model.load_state(todo_uuid)
    return model.get_schema()


@app.put("/wallet/{todo_uuid}", response_model=Wallet)
def handle_update(todo_uuid: str, item: Wallet, db: Session = Depends(get_db)):
    model = domain.WalletDomainModel(db=db, item_id=item.id)
    model.load_state(todo_uuid)
    model.handle(WalletUpdatedEvent(title=item.title))
    return model.get_schema()
