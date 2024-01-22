from fastapi import status, HTTPException
from pydantic import BaseModel


class ExceptionResponse:
    @property
    def auth(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    @property
    def not_found(self) -> HTTPException:
        return HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found",
        )


class StandardResponse(BaseModel):
    status_code: int
    message: str | None
    data: object | None

    def __init__(self, status_code: int = 200, message: str | None = None, data: object | None = None):
        super().__init__(status_code=status_code, message=message, data=data)
