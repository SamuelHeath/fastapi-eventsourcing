import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.main import app, get_db
from app.schemas import WalletEventCreate, Wallet

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


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_create_wallet(cleanup):
    wec = WalletEventCreate(title="test_user wallet")
    response = client.post("/wallet", data=wec.json())

    assert response.status_code == 201
    assert Wallet(**response.json()).dict(include={"title"}) == {"title": wec.title}


def test_update_wallet(cleanup):
    wec = WalletEventCreate(title="test_user wallet")
    response = client.post("/wallet", data=wec.json())

    wallet = Wallet(**response.json())
    wallet.title = "New Wallet"
    response = client.put(f"/wallet/{wallet.entity_id}", data=wallet.json())
    assert response.status_code == 200
    assert Wallet(**response.json()).dict(include={"title"}) == {"title": wallet.title}
