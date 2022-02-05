from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSON

from database import Base


class TodoItemEvent(Base):
    __tablename__ = "items"

    uuid = Column(String, primary_key=True)
    entity_id = Column(String, index=True)
    sequence_id = Column(Integer)
    data = Column(JSON)
