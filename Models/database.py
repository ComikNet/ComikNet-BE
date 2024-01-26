from sqlalchemy import Column, INT, TEXT, TIMESTAMP

from Services.Database.database import Base


class UserDb(Base):
    __tablename__ = "user"
    id = Column(INT, unique=True, primary_key=True, index=True, nullable=False)
    uid = Column(TEXT, unique=True, index=True, nullable=False)
    username = Column(TEXT, unique=True, index=True, nullable=False)
    email = Column(TEXT, unique=True, nullable=False)
    hashed_password = Column(TEXT, nullable=False)
    created_at = Column(TIMESTAMP, nullable=False)


class PwdDb(Base):
    __tablename__ = "src_pwd"
    id = Column(INT, unique=True, primary_key=True, index=True, nullable=False)
    source = Column(TEXT, index=True, nullable=False)
    uid = Column(TEXT, index=True, nullable=False)
    account = Column(TEXT, nullable=False)
    pwd = Column(TEXT, nullable=False)
