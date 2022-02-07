from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSON

from app.database import Base


class WalletEvent(Base):
    __tablename__ = "wallet"

    uuid = Column(String, primary_key=True)
    entity_id = Column(String, index=True)
    data = Column(JSON)
