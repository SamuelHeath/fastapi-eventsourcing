from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# POSTGRESQL_DB_URL = "postgresql://postgres:test@db/todo"
POSTGRESQL_DB_URL = "postgresql://postgres:test@0.0.0.0/todo"

engine = create_engine(
    POSTGRESQL_DB_URL,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
