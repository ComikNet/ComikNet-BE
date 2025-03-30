import json
from datetime import datetime, timedelta
from uuid import uuid4

import bcrypt
from fastapi import APIRouter, Depends, Form, Header, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from Models.database import PwdDb, UserDb
from Models.plugins import IAuth
from Models.requests import SourceStorageReq
from Models.response import BaseResponse, PluginResponse, StandardResponse
from Models.user import Token, TokenData, User, UserData
from Services.Cache.cache import cache
from Services.Database.database import get_db
from Services.Limiter.limiter import freq_limiter
from Services.Mail.mail import Purpose, get_normalized_email, send_captcha
from Services.Modulator.manager import plugin_manager
from Services.Security.user import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    create_access_token,
    decrypt_src_data,
    encrypt_src_data,
    get_current_user,
    get_user_data,
)

user_router = APIRouter(prefix="/user")


@user_router.get("/captcha/register", response_model=BaseResponse[str])
@freq_limiter.limit("1/minute")
async def user_req_register_captcha(
    request: Request, email: str
) -> StandardResponse[str]:
    normalized_email = get_normalized_email(email)
    ip = request.client.host if request.client else "Unknown"
    captcha = send_captcha(normalized_email, Purpose.REGISTER, ip)
    request_id = uuid4().hex
    await cache.set(key=f"{normalized_email}_{request_id}", value=captcha, ttl=300)
    return StandardResponse[str](message="Captcha sent", data=request_id)


@user_router.get("/captcha/recover", response_model=BaseResponse[str])
@freq_limiter.limit("1/minute")
async def user_req_recover_captcha(
    request: Request, email: str
) -> StandardResponse[str]:
    normalized_email = get_normalized_email(email)
    ip = request.client.host if request.client else "Unknown"
    captcha = send_captcha(normalized_email, Purpose.RECOVER_PASSWORD, ip)
    request_id = uuid4().hex
    await cache.set(key=f"{normalized_email}_{request_id}", value=captcha, ttl=300)
    return StandardResponse[str](message="Captcha sent", data=request_id)


@user_router.post("/register", response_model=BaseResponse, status_code=201)
@freq_limiter.limit("10/minute")
async def user_reg(
    request: Request,
    email: str = Form(),
    username: str = Form(),
    password: str = Form(),
    captcha: str = Form(),
    request_id: str = Header(convert_underscores=True),
    db: Session = Depends(get_db),
) -> StandardResponse[None]:
    normalized_email = get_normalized_email(email)
    if password.strip().__len__() < 6:
        raise HTTPException(status_code=400, detail="Password too short")
    if (
        db.query(UserDb)
        .filter((UserDb.email == normalized_email) | (UserDb.username == username))
        .first()
        is not None
    ):
        raise HTTPException(status_code=409, detail="User already exists")

    if (
        cached_captcha := await cache.get(f"{normalized_email}_{request_id}")
    ) is None or cached_captcha != captcha:
        raise HTTPException(status_code=400, detail="Invalid captcha")

    await cache.delete(f"{normalized_email}_{request_id}")

    db.add(
        UserDb(
            user_id=uuid4().hex,
            email=email,
            username=username,
            password=bcrypt.hashpw(bytes(password, "utf-8"), bcrypt.gensalt()).decode(),
            created_at=datetime.now(),
        )
    )
    db.commit()
    return StandardResponse[None](status_code=201, message="User created")


@user_router.post("/login", response_model=BaseResponse[Token])
@freq_limiter.limit("10/minute")
def user_login(
    request: Request,
    body: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> StandardResponse[Token]:
    user: UserDb | None = (
        db.query(UserDb).filter(UserDb.username == body.username).first()
    )

    if user is None or not bcrypt.checkpw(
        bytes(body.password, "utf-8"), bytes(user.password, "utf-8")
    ):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    token = create_access_token(
        data=TokenData(sub=user.username, id=user.user_id),
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return StandardResponse[Token](data=Token(access_token=token, token_type="bearer"))


@user_router.post("/recover", response_model=BaseResponse)
@freq_limiter.limit("10/minute")
async def user_recover(
    request: Request,
    email: str = Form(),
    password: str = Form(),
    captcha: str = Form(),
    request_id: str = Header(convert_underscores=True),
    db: Session = Depends(get_db),
) -> StandardResponse[str]:
    if (record := db.query(UserDb).filter(UserDb.email == email).first()) is None:
        raise HTTPException(status_code=404, detail="User not found")

    normalized_email = get_normalized_email(email)
    if password.strip().__len__() < 6:
        raise HTTPException(status_code=400, detail="Password too short")

    if (
        cached_captcha := await cache.get(f"{normalized_email}_{request_id}")
    ) is None or cached_captcha != captcha:
        raise HTTPException(status_code=400, detail="Invalid captcha")

    await cache.delete(f"{normalized_email}_{request_id}")

    record.password = bcrypt.hashpw(bytes(password, "utf-8"), bcrypt.gensalt()).decode(
        "utf-8"
    )
    username = record.username
    db.commit()

    return StandardResponse[str](message="Password recovered", data=username)


@user_router.get("/profile", response_model=BaseResponse[User])
def user_profile(
    user: User = Depends(get_current_user),
) -> StandardResponse[User]:
    return StandardResponse[User](data=user)


@user_router.get("/{src}/login", response_model=BaseResponse[PluginResponse])
def user_src_auth_info(src: str):
    if (source := plugin_manager.get_source(src)) is None:
        raise HTTPException(status_code=404, detail="Source not found")

    if not isinstance(source.instance, IAuth):
        return StandardResponse[PluginResponse](data=PluginResponse(required=False))

    return StandardResponse[PluginResponse](
        data=PluginResponse(required=True, items=source.service.get("login"))
    )


@user_router.post("/{src}/login", response_model=BaseResponse[object])
async def user_src_login(
    response: Response,
    src: str,
    body: dict[str, str],
    user_data: UserData = Depends(get_user_data),
) -> StandardResponse[object]:
    if (source := plugin_manager.get_source(src)) is None:
        raise HTTPException(status_code=404, detail="Source not found")

    if not isinstance(source.instance, IAuth):
        raise HTTPException(status_code=400, detail="Invalid source")

    result = await source.instance.login(body, user_data)
    if result.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Failed to login to source {src}")

    response.set_cookie(key="plugin_data", value=user_data.__str__())
    return result


@user_router.post("/{src_id}/encrypt", response_model=BaseResponse)
async def user_encrypt_src_data(
    src: str,
    body: SourceStorageReq,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    user_data: UserData = Depends(get_user_data),
) -> StandardResponse[None]:
    if (source := plugin_manager.get_source(src)) is None:
        raise HTTPException(status_code=404, detail="Source not found")

    if not isinstance(source.instance, IAuth) or not source.instance.auto_login:
        raise HTTPException(status_code=400, detail="Invalid source")

    if (
        record := db.query(PwdDb)
        .filter(PwdDb.source == src, PwdDb.user_id == user.user_id)
        .first()
    ) is not None:
        result = await source.instance.login(body.data, user_data)
        if result.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid source data")

        record.data = encrypt_src_data(body.password, body.data.__str__())
    else:
        db.add(
            PwdDb(
                user_id=user.user_id,
                source=src,
                data=encrypt_src_data(body.password, body.data.__str__()),
            )
        )

    db.commit()
    return StandardResponse[None](message=f"{src} auth data saved")


@user_router.post("/{src}/auto_login", response_model=BaseResponse[object])
async def user_src_autologin(
    response: Response,
    src: str,
    password: str = Form(),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    user_data: UserData = Depends(get_user_data),
) -> StandardResponse[object]:
    if (source := plugin_manager.get_source(src)) is None:
        raise HTTPException(status_code=404, detail="Source not found")

    if (
        not isinstance(source.instance, IAuth)
        or not isinstance(source.service.get("login"), list)
        or source.service["login"] == []
    ):
        raise HTTPException(status_code=400, detail="Invalid source")

    if (
        record := db.query(PwdDb)
        .filter(PwdDb.source == src, PwdDb.user_id == user.user_id)
        .first()
    ) is None:
        raise HTTPException(status_code=404, detail="Source user not found")

    data = json.loads(decrypt_src_data(password, record.data))

    result = await source.instance.login(data, user_data)
    if result.status_code != 200:
        raise HTTPException(
            status_code=400, detail=f"Failed to auto login to source {src}"
        )

    response.set_cookie(key="plugin_data", value=user_data.__str__())
    return result
