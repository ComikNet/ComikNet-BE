from fastapi import status, HTTPException, Request
from pydantic import BaseModel
from slowapi.errors import RateLimitExceeded


class ExceptionResponse:
    auth = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    not_found = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Not found",
    )

    @staticmethod
    def limit_exceeded(request: Request, exc: RateLimitExceeded):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests",
            headers={"Detail": exc.detail},
        )


class StandardResponse[T](BaseModel):
    """
    Standard Response Model
    ~~~~~~~~~~~~~~~~~~~~~
    This model is the default web response format of the API.
    """

    status_code: int
    message: str | None
    data: T | None

    def __init__(
        self, status_code: int = 200, message: str | None = None, data: T | None = None
    ):
        super().__init__(status_code=status_code, message=message, data=data)
