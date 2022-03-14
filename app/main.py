import redis
from fastapi import FastAPI, BackgroundTasks
from fastapi.params import Depends
from sqlalchemy.orm import Session
from starlette import status

from app import domain
from app import models
from app.cache import Cache, RedisCache
from app.database import SessionLocal, engine
from app.schemas import (
    Wallet,
    WalletCreatedEventIn,
    WalletCreateEvent,
    WalletUpdateEvent,
    WalletDebitEvent,
    WalletDebitEventIn,
    WalletCreditEventIn,
    WalletCreditEvent,
)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_cache() -> Cache:
    cache = RedisCache(redis.Redis(host="redis", port=6379, db=0))
    try:
        yield cache
    finally:
        pass


def save_wallet_state(cache: Cache, wallet: Wallet):
    try:
        cache.set(wallet.entity_id, wallet.json())
        print("saved")
    except Exception:
        print("failed")
        pass


@app.post("/wallet", response_model=Wallet, status_code=status.HTTP_201_CREATED)
def handle_create(
        create_event: WalletCreatedEventIn,
        background_tasks: BackgroundTasks,
        cache: Cache = Depends(get_cache),
        db: Session = Depends(get_db),
):
    try:
        model = domain.WalletDomainModel(db=db)
        state = model.handle(WalletCreateEvent(**create_event.dict()))

        background_tasks.add_task(save_wallet_state, cache, state)
        db.commit()
        return state
    except Exception as e:
        db.rollback()
        raise e


@app.get("/wallet/{wallet_id}", response_model=Wallet, status_code=status.HTTP_200_OK)
def handle_id(
        wallet_id: str,
        background_tasks: BackgroundTasks,
        cache: Cache = Depends(get_cache),
        db: Session = Depends(get_db),
):
    result = cache.get(wallet_id)
    if result is not None:
        return Wallet.parse_raw(result)

    model = domain.WalletDomainModel(db=db, item_id=wallet_id)
    model.load_state(wallet_id)

    state = model.get_state()
    background_tasks.add_task(save_wallet_state, cache, state)
    return state


@app.put("/wallet/{wallet_id}", response_model=Wallet, status_code=status.HTTP_200_OK)
def handle_update(wallet_id: str, item: Wallet, db: Session = Depends(get_db)):
    try:
        model = domain.WalletDomainModel(db=db, item_id=item.entity_id)
        model.load_state(wallet_id)
        state = model.handle(WalletUpdateEvent(title=item.title))
        db.commit()
        return state
    except Exception as e:
        db.rollback()
        raise e


@app.post(
    "/wallet/{wallet_id}/deposit",
    response_model=Wallet,
    status_code=status.HTTP_201_CREATED,
)
def handle_id(
        wallet_id: str, deposit_event: WalletDebitEventIn, db: Session = Depends(get_db)
):
    try:
        model = domain.WalletDomainModel(db=db, item_id=wallet_id)
        model.load_state(wallet_id)
        state = model.handle(WalletDebitEvent(**deposit_event.dict()))
        db.commit()
        return state
    except Exception as e:
        db.rollback()
        raise e


@app.post(
    "/wallet/{wallet_id}/credit",
    response_model=Wallet,
    status_code=status.HTTP_201_CREATED,
)
def handle_id(
        wallet_id: str, deposit_event: WalletCreditEventIn, db: Session = Depends(get_db)
):
    try:
        model = domain.WalletDomainModel(db=db, item_id=wallet_id)
        model.load_state(wallet_id)
        state = model.handle(WalletCreditEvent(**deposit_event.dict()))
        db.commit()
        return state
    except Exception as e:
        db.rollback()
        raise e
