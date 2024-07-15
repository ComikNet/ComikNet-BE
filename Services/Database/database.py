from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from Configs.config import config

protocol = config.get_config("database", "protocol")
host = config.get_config("database", "host")
port = config.get_config("database", "port")
db = config.get_config("database", "database")
user = config.get_config("database", "user")
pwd = config.get_config("database", "password")
auth = f"{user}:{pwd}@" if user and pwd else ""
if not host or not port or not db:
    raise ValueError("Please complete the database configuration")

engine = create_engine(f"{protocol}://{auth}{host}:{port}/{db}")
SessionLocal = sessionmaker(autocommit=False, bind=engine)
Base = declarative_base()


def get_db():
    database = SessionLocal()
    try:
        yield database
    finally:
        database.close()
