from sqlalchemy import Column, String, Integer, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSON

from app.database import Base


class WalletEvent(Base):
    __tablename__ = "wallet"

    uuid = Column(String, primary_key=True)
    entity_id = Column(String, index=True)
    sequence_id = Column(Integer, default=0)
    data = Column(JSON)

    UniqueConstraint('entity_id', 'sequence_id', name='entity_sequence_uniq')
