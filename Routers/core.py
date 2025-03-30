from fastapi import APIRouter
from Models.response import BaseResponse, StandardResponse

core_router = APIRouter(prefix="/core")


@core_router.get("/ping", response_model=BaseResponse)
def get_status() -> StandardResponse[None]:
    return StandardResponse(message="pong")


@core_router.get("/protocol", response_model=BaseResponse[str])
def get_cnm_version() -> StandardResponse[str]:
    return StandardResponse[str](data="0.2.1")
