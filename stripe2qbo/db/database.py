import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

POSTGRES_URI = os.getenv("POSTGRES_URI")
print(POSTGRES_URI)
connect_args = {}

if POSTGRES_URI is None:
    db_engine = "sqlite:///./stripe2qbo.db"
    connect_args["check_same_thread"] = False
else:
    db_engine = f"{POSTGRES_URI}"

engine = create_engine(db_engine, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
