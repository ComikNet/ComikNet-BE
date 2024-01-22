from datetime import timedelta, datetime, UTC
import os
from jose import jwt, JWTError
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

from Services.Database.database import get_db
from Models.database import UserDb
from Models.user import User
from Models.response import ExceptionResponse

SECRET_KEY: str | None = os.environ.get("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

if not SECRET_KEY or SECRET_KEY.__len__() < 32:
    raise ValueError(
        "Please set `SECRET_KEY` environment variable, you can generate one with `openssl rand -hex 32`"
    )

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid: str = payload["id"]
        if uid is None:
            raise ExceptionResponse.auth
    except JWTError:
        raise ExceptionResponse.auth

    user: UserDb = db.query(UserDb).filter(UserDb.uid == uid).first()  # type: ignore
    if user is None:
        raise ExceptionResponse.auth

    return User(uid=user.uid, email=user.email, username=user.username, created_at=user.created_at)


def encrypt_src_password(key: str, src_pwd: str) -> str:
    cipher = AES.new(pad(key.encode("utf-8"), AES.block_size), AES.MODE_ECB)
    return cipher.encrypt(pad(src_pwd.encode("utf-8"), AES.block_size)).hex()


def decrypt_src_password(key: str, encrypted_pwd: str) -> str:
    cipher = AES.new(pad(key.encode("utf-8"), AES.block_size), AES.MODE_ECB)
    return unpad(cipher.decrypt(bytes.fromhex(encrypted_pwd)), AES.block_size).decode("utf-8")
