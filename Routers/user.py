from fastapi import APIRouter, Response, Depends, HTTPException, Form
from fastapi.security import OAuth2PasswordRequestForm
from passlib.context import CryptContext
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from uuid import uuid4
from datetime import datetime, timedelta

from Services.Database.database import get_db
from Services.Security.user import ACCESS_TOKEN_EXPIRE_MINUTES, create_access_token, get_current_user
from Models.database import UserDb
from Models.user import Token

user_router = APIRouter(prefix="/user")
pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


@user_router.post("/reg")
async def user_reg(email: str = Form(), username: str = Form(), password: str = Form(), db: Session = Depends(get_db)):
    try:
        db.add(UserDb(
            uid=uuid4().hex,
            email=email,
            username=username,
            hashed_password=pwd_ctx.hash(password),
            created_at=datetime.now(),
        )
        )
        db.commit()
        return Response(status_code=201)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="User already exists")


@user_router.post("/login")
async def user_login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user: UserDb = db.query(UserDb).filter(UserDb.username == body.username).first()
    if user is not None and pwd_ctx.verify(body.password, user.hashed_password):
        token = create_access_token(
            data={"sub": user.email, "id": user.uid},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        return Token(access_token=token, token_type="bearer")
    else:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


@user_router.get("/profile")
async def user_profile(user: UserDb = Depends(get_current_user)):
    return user
