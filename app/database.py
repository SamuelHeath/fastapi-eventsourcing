import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# POSTGRESQL_DB_URL = "postgresql://postgres:test@0.0.0.0/todo"
POSTGRESQL_DB_URL = "postgresql://postgres:test@db/todo"


def get_engine():
    if os.getenv("TESTING", "0") == "1":
        SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
        return create_engine(
            SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
        )

    else:
        return create_engine(
            POSTGRESQL_DB_URL,
        )


engine = get_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
