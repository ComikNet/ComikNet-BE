import logging
import typing

import sqlalchemy

from sqlalchemy import Column, Text
from Models.plugins import IAuth
from fastapi import APIRouter, Response, Depends, HTTPException, Form, Request
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime, timedelta

from Services.Database.database import get_db
from Services.Modulator.manager import plugin_manager
from Services.Limiter.limiter import limiter
from Services.Security.user import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    get_current_user,
    encrypt_src_password,
    decrypt_src_password,
)
from Models.database import UserDb, PwdDb
from Models.user import Token, User
from Models.response import ExceptionResponse, StandardResponse
from Models.requests import SourceStorageReq
from Utils.convert import sql_typecast

user_router = APIRouter(prefix="/user")
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
logger = logging.getLogger(__name__)


@user_router.post("/reg")
@limiter.limit("5/minute")
async def user_reg(
    request: Request,
    email: str = Form(),
    username: str = Form(),
    password: str = Form(),
    db: Session = Depends(get_db),
):
    if (
        db.query(UserDb)
        .filter(UserDb.email == email or UserDb.username == username)
        .first()
        is not None
    ):
        raise HTTPException(status_code=409, detail="User already exists")

    db.add(
        UserDb(
            uid=uuid4().hex,
            email=email,
            username=username,
            hashed_password=pwd_ctx.hash(password),
            created_at=datetime.now(),
        )
    )
    db.commit()
    return Response(status_code=201)


@user_router.post("/login")
@limiter.limit("5/minute")
async def user_login(
    body: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user: UserDb | None = (
        db.query(UserDb).filter(UserDb.username == body.username).first()
    )

    if user is not None and pwd_ctx.verify(body.password, user.hashed_password):
        token = create_access_token(
            data={"sub": user.email, "id": user.uid},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return Token(access_token=token, token_type="bearer")
    else:
        raise ExceptionResponse.auth


@user_router.get("/profile")
async def user_profile(user: User = Depends(get_current_user)):
    return StandardResponse(data=user)


@user_router.get("/{src}/login")
async def src_login_info(src: str):
    if (source := plugin_manager.get_source(src)) is None or not isinstance(
        source.instance, IAuth
    ):
        raise ExceptionResponse.not_found

    return StandardResponse(data={"required": True, "items": source.service["login"]})


@user_router.post("/{src}/login")
async def src_login(src: str, body: dict[str, str]):
    if (source := plugin_manager.get_source(src)) is None or not isinstance(
        source.instance, IAuth
    ):
        raise ExceptionResponse.not_found

    if (
        not isinstance(source.service.get("login"), list)
        or source.service["login"] == []
    ):
        raise ExceptionResponse.not_found

    result = source.instance.login(body)


@user_router.post("/{src_id}/encrypt")
async def encrypt_src_pwd(
    src_id: str,
    body: SourceStorageReq,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    record: PwdDb | None = (
        db.query(PwdDb)
        .filter(
            PwdDb.src_id == src_id
            and PwdDb.uid == user.uid
            and PwdDb.account == body.account
        )
        .first()
    )

    if record is None:
        db.add(
            PwdDb(
                src_id=src_id,
                uid=user.uid,
                account=body.account,
                pwd=encrypt_src_password(body.key_pwd, body.src_pwd),
            )
        )
        db.commit()
        return Response(status_code=201)
    else:
        record.pwd = sql_typecast(
            encrypt_src_password(body.key_pwd, body.src_pwd), Column[typing.Text]
        )
        db.commit()
        return Response(status_code=200)


@user_router.get("/{src}/accounts")
async def get_src_accounts(
    src: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)
):
    records: list[PwdDb] = (
        db.query(PwdDb).filter(PwdDb.src_id == src and PwdDb.uid == user.uid).all()
    )

    return StandardResponse(data=[record.account for record in records])


@user_router.get("/{src}/decrypt")
async def decrypt_src_pwd(
    src: str,
    account: str,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    record: PwdDb | None = (
        db.query(PwdDb)
        .filter(
            PwdDb.src_id == src and PwdDb.uid == user.uid and PwdDb.account == account
        )
        .first()
    )

    if record is None:
        raise ExceptionResponse.not_found
    else:
        return StandardResponse(data=decrypt_src_password(record.pwd, record.src_id))
