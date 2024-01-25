from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from Configs.config import config

host = config.get_config("database", "host")
port = config.get_config("database", "port")
db = config.get_config("database", "database")
user = config.get_config("database", "user")
pwd = config.get_config("database", "password")
if not host or not port or not db or not user or not pwd:
    raise ValueError("Please complete the database configuration")

engine = create_engine(f"postgresql://{user}:{pwd}@{host}:{port}/{db}")
SessionLocal = sessionmaker(autocommit=False, bind=engine)
Base = declarative_base()


def get_db():
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()
