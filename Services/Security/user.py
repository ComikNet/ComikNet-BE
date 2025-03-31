from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
from fastapi import Cookie, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from sqlalchemy.orm import Session

from Models.database import UserDb
from Models.user import TokenData, User, UserData
from Services.Config.config import config
from Services.Database.database import get_db
from Services.Modulator.manager import PluginUtils

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
SECRET_KEY = config.security.secret_key


def create_access_token(data: TokenData, expires_delta: timedelta | None = None) -> str:
    to_encode = data.model_copy()
    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.exp = expire
    encoded_jwt = jwt.encode(to_encode.model_dump(), SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        uid: str = payload["id"]
        if uid is None:
            raise InvalidTokenError
    except InvalidTokenError:
        raise HTTPException(
            401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user: UserDb | None = db.query(UserDb).filter(UserDb.uid == uid).first()
    if user is None:
        raise HTTPException(
            401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return User(
        user_id=user.uid,
        email=user.email,
        username=user.username,
        created_at=user.created_at,
    )


def get_user_data(
    plugin_cookies: Annotated[str | None, Cookie()] = None,
    user: User = Depends(get_current_user),
):
    return UserData(
        uid=user.user_id, plugin_cookies=PluginUtils.load_cookies(plugin_cookies)
    )


def encrypt_src_data(key: str, src_data: str) -> str:
    iv = get_random_bytes(AES.block_size)
    cipher = AES.new(pad(key.encode("utf-8"), AES.block_size), AES.MODE_CBC, iv)
    encrypted_data = iv + cipher.encrypt(pad(src_data.encode("utf-8"), AES.block_size))
    return encrypted_data.hex()


def decrypt_src_data(key: str, encrypted_data: str) -> str:
    encrypted_data_bytes = bytes.fromhex(encrypted_data)
    iv = encrypted_data_bytes[: AES.block_size]
    cipher = AES.new(pad(key.encode("utf-8"), AES.block_size), AES.MODE_CBC, iv)
    decrypted_data = unpad(
        cipher.decrypt(encrypted_data_bytes[AES.block_size :]), AES.block_size
    )
    return decrypted_data.decode("utf-8")
