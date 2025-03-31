from fastapi import APIRouter

from Models.response import BaseResponse, StandardResponse
from Services.Modulator.manager import plugin_manager

core_router = APIRouter(prefix="/core")


@core_router.get("/ping", response_model=BaseResponse)
def get_status() -> StandardResponse[None]:
    return StandardResponse(message="pong")


@core_router.get("/sources", response_model=BaseResponse[set[str]])
def get_sources() -> StandardResponse[set[str]]:
    sources = plugin_manager.registered_source
    return StandardResponse[set[str]](data=sources)


@core_router.get("/protocol", response_model=BaseResponse[str])
def get_cnm_version() -> StandardResponse[str]:
    return StandardResponse[str](data=plugin_manager.cnm_version.__str__())
