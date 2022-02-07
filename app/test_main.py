from fastapi.testclient import TestClient

from app import main
from app.schemas import WalletEventCreate, Wallet

client = TestClient(main.app)


def test_create_wallet():
    wec = WalletEventCreate(title="test_user wallet")
    response = client.post("/wallet", data=wec.json())

    assert response.status_code == 200
    assert Wallet(**response.json()).dict(include={"title"}) == {"title": wec.title}
