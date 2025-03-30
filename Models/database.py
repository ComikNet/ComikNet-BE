from datetime import datetime

from sqlalchemy import DATE, TEXT, VARCHAR, PrimaryKeyConstraint
from sqlalchemy.orm import Mapped, mapped_column

from Services.Database.database import Base


class UserDb(Base):
    __tablename__ = "user"
    user_id: Mapped[str] = mapped_column(VARCHAR(32), primary_key=True)
    username: Mapped[str] = mapped_column(TEXT, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(TEXT, nullable=False)
    password: Mapped[str] = mapped_column(TEXT, nullable=False)
    created_at: Mapped[datetime | None] = mapped_column(DATE, nullable=True)


class PwdDb(Base):
    __tablename__ = "src_pwd"
    __table_args__ = PrimaryKeyConstraint("user_id", "source")
    user_id: Mapped[str] = mapped_column(VARCHAR(32), nullable=False)
    source: Mapped[str] = mapped_column(TEXT, nullable=False)
    data: Mapped[str] = mapped_column(TEXT, nullable=False)
