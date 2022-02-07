from fastapi import FastAPI
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette import status

from app import domain
from app import models
from app.database import SessionLocal, engine
from app.schemas import Wallet, WalletEventCreate, WalletCreatedEvent, WalletUpdatedEvent, WalletDepositEvent, WalletEventDeposit

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


@app.post("/wallet", response_model=Wallet, status_code=status.HTTP_201_CREATED)
def handle_create(create_event: WalletEventCreate, db: Session = Depends(get_db)):
    model = domain.WalletDomainModel(db=db)
    model.handle(WalletCreatedEvent(**create_event.dict()))
    return model.get_schema()


@app.get("/wallet/{wallet_id}", response_model=Wallet, status_code=status.HTTP_200_OK)
def handle_id(wallet_id: str, db: Session = Depends(get_db)):
    model = domain.WalletDomainModel(db=db, item_id=wallet_id)
    model.load_state(wallet_id)
    return model.get_schema()


@app.put("/wallet/{wallet_id}", response_model=Wallet, status_code=status.HTTP_200_OK)
def handle_update(wallet_id: str, item: Wallet, db: Session = Depends(get_db)):
    model = domain.WalletDomainModel(db=db, item_id=item.entity_id)
    model.load_state(wallet_id)
    model.handle(WalletUpdatedEvent(title=item.title))
    return model.get_schema()


@app.post("/wallet/{wallet_id}/deposit", response_model=Wallet, status_code=status.HTTP_201_CREATED)
def handle_id(wallet_id: str, deposit_event: WalletEventDeposit, db: Session = Depends(get_db)):
    model = domain.WalletDomainModel(db=db, item_id=wallet_id)
    model.load_state(wallet_id)
    model.handle(WalletDepositEvent(**deposit_event.dict()))
    return model.get_schema()
