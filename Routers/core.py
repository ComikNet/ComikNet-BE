from fastapi import APIRouter, Response, Depends, HTTPException, Form, Request

from Models.user import User
from Models.requests import ComicSearchReq
from Models.response import ExceptionResponse, StandardResponse
from Services.Database.database import get_db
from Services.Limiter.limiter import limiter
from Services.Security.user import get_current_user
from Services.Modulator.manager import plugin_manager

core_router = APIRouter(prefix="/core")


@core_router.get("/ping")
async def get_status():
    return StandardResponse(message="pong")

@core_router.get("/protocol")
async def get_cnm_version():
    pass