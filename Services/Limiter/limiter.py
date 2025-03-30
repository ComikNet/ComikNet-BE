from fastapi import Request
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.types import ASGIApp

from Models.response import HTTPException

freq_limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


async def RateLimitExceeded_handler(request: Request, exc: RateLimitExceeded):
    raise HTTPException(429, f"Rate limit exceeded: {exc.detail}")


# -*- author: abdusco<https://github.com/abdusco> -*-
class LimitUploadSize(BaseHTTPMiddleware):
    def __init__(self, app: ASGIApp, max_upload_size: int) -> None:
        super().__init__(app)
        self.max_upload_size = max_upload_size

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        if request.method == "POST":
            if "content-length" not in request.headers:
                raise HTTPException(411, "Content-Length header is required")
            content_length = int(request.headers["content-length"])
            if content_length > self.max_upload_size:
                raise HTTPException(
                    status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    f"Request body is too large: {content_length} > {self.max_upload_size}",
                )
        return await call_next(request)
