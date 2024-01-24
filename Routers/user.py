from fastapi import APIRouter, Response, Depends, HTTPException, Form, Request
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime, timedelta

from Services.Database.database import get_db
from Services.Limiter.limiter import limiter
from Services.Security.user import (
    ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_user,
    encrypt_src_password, decrypt_src_password)
from Models.database import UserDb, PwdDb
from Models.user import Token, User
from Models.response import ExceptionResponse, StandardResponse
from Models.requests import SourceStorageReq

user_router = APIRouter(prefix="/user")
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


@user_router.post("/reg")
@limiter.limit("5/minute")
async def user_reg(request: Request, email: str = Form(), username: str = Form(), password: str = Form(),
                   db: Session = Depends(get_db)):
    if db.query(UserDb).filter(
            UserDb.email == email or UserDb.username == username).first() is not None:  # type: ignore
        raise HTTPException(status_code=409, detail="User already exists")

    db.add(UserDb(
        uid=uuid4().hex,
        email=email,
        username=username,
        hashed_password=pwd_ctx.hash(password),
        created_at=datetime.now(),
    ))
    db.commit()
    return Response(status_code=201)


@user_router.post("/login")
@limiter.limit("5/minute")
async def user_login(request: Request, body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user: UserDb = db.query(UserDb).filter(UserDb.username == body.username).first()  # type: ignore
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


@user_router.post("/encrypt/{src_id}")
async def encrypt_src_pwd(src_id: str, body: SourceStorageReq, db: Session = Depends(get_db),
                          user: User = Depends(get_current_user)):
    record: PwdDb = db.query(PwdDb).filter(
        PwdDb.src_id == src_id and PwdDb.uid == user.uid and PwdDb.account == body.account).first()  # type: ignore

    if record is None:
        db.add(PwdDb(src_id=src_id, uid=user.uid, account=body.account,
                     pwd=encrypt_src_password(body.key_pwd, body.src_pwd)))
        db.commit()
        return Response(status_code=201)
    else:
        record.pwd = encrypt_src_password(body.key_pwd, body.src_pwd)
        db.commit()
        return Response(status_code=200)


@user_router.get("/accounts/{src_id}")
async def get_src_accounts(src_id: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    records: list[PwdDb] = db.query(PwdDb).filter(
        PwdDb.src_id == src_id and PwdDb.uid == user.uid).all()  # type: ignore

    return StandardResponse(data=[record.account for record in records])


@user_router.get("/decrypt/{src_id}")
async def decrypt_src_pwd(src_id: str, account: str, db: Session = Depends(get_db),
                          user: User = Depends(get_current_user)):
    record: PwdDb = db.query(PwdDb).filter(
        PwdDb.src_id == src_id and PwdDb.uid == user.uid and PwdDb.account == account).first()  # type: ignore

    if record is None:
        raise ExceptionResponse.not_found
    else:
        return StandardResponse(data=decrypt_src_password(record.pwd, record.src_id))
