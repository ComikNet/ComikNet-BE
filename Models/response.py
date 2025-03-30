from fastapi import HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class BaseResponse[T](BaseModel):
    """
    Base Response Class
    ~~~~~~~~~~~~~~~~~~~~~~
    This class is the base response of the API.
    """

    status_code: int
    message: str | None = None
    data: T | None = None


class StandardResponse[T](JSONResponse):
    """
    Standard Response Class
    ~~~~~~~~~~~~~~~~~~~~~~
    This class is the default web response of the API.
    """

    def __init__(
        self,
        status_code: int = 200,
        message: str | None = None,
        data: T | None = None,
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(
            content=BaseResponse[T](
                status_code=status_code, message=message, data=data
            ).model_dump(mode="json"),
            status_code=status_code,
            headers=headers,
        )


class PluginResponse(BaseModel):
    required: bool
    items: list[str] | None = None


async def http_exception_handler(
    request: Request, exc: HTTPException
) -> StandardResponse[None]:
    return StandardResponse[None](
        status_code=exc.status_code, message=exc.detail, data=None
    )


async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> StandardResponse[object]:
    return StandardResponse[object](
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        message="Invalid request data structure.",
        data=jsonable_encoder(exc.errors()),
    )
