from datetime import datetime
from pydantic import BaseModel


class User(BaseModel):
    uid: str
    email: str
    username: str
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str
