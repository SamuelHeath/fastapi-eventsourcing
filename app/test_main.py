import uuid

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models
from app.database import Base
from app.domain import WalletDomainModel
from app.main import app, get_db
from app.schemas import WalletEventCreate, Wallet, WalletCreatedEvent, WalletDebitEvent, WalletCreditEvent

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def cleanup():
    Base.metadata.create_all(bind=engine)
    yield None
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def create_wallet(cleanup):
    event = WalletCreatedEvent(title="Example Wallet")
    _wallet = models.WalletEvent(uuid=event.uuid, entity_id=str(uuid.uuid4()), data=event.json(exclude={"uuid"}))
    db = next(override_get_db())
    db.add(_wallet)
    db.commit()
    db.refresh(_wallet)
    model = WalletDomainModel(db=db, item_id=_wallet.entity_id)
    model.load_state()
    yield model.get_schema()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_create_wallet(cleanup):
    wec = WalletEventCreate(title="test_user wallet")
    response = client.post("/wallet", data=wec.json())

    assert response.status_code == 201
    assert Wallet(**response.json()).dict(include={"title"}) == {"title": wec.title}


def test_update_wallet(cleanup, create_wallet):
    wallet = create_wallet
    wallet.title = "New Wallet"
    response = client.put(f"/wallet/{wallet.entity_id}", data=wallet.json())
    assert response.status_code == 200
    assert Wallet(**response.json()).dict(include={"title"}) == {"title": wallet.title}


def test_deposit_wallet(cleanup, create_wallet):
    wallet = create_wallet
    wde = WalletDebitEvent(amount=50.0)
    response = client.post(f"/wallet/{wallet.entity_id}/deposit", data=wde.json())

    assert response.status_code == 201
    assert Wallet(**response.json()).dict(include={"amount"}) == {"amount": 50.0}


def test_credit_wallet(cleanup, create_wallet):
    wallet = create_wallet
    wce = WalletCreditEvent(amount=50.0)
    response = client.post(f"/wallet/{wallet.entity_id}/credit", data=wce.json())
    assert response.status_code == 400

    wde = WalletDebitEvent(amount=50.0)
    client.post(f"/wallet/{wallet.entity_id}/deposit", data=wde.json())
    wce = WalletCreditEvent(amount=45.0)
    response = client.post(f"/wallet/{wallet.entity_id}/credit", data=wce.json())

    assert response.status_code == 201
    assert Wallet(**response.json()).dict(include={"amount"}) == {"amount": 5.0}
