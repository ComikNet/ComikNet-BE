from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

from Models.response import http_exception_handler, validation_exception_handler
from Routers.comic import comic_router
from Routers.user import user_router
from Services.Database.database import Base, engine
from Services.Limiter.limiter import (
    LimitUploadSize,
    RateLimitExceeded_handler,
    freq_limiter,
)
from Services.Modulator.manager import plugin_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine, checkfirst=True)
    yield


app = FastAPI()

app.state.limiter = freq_limiter  # type: ignore
app.add_exception_handler(RateLimitExceeded, RateLimitExceeded_handler)  # type: ignore
app.add_exception_handler(HTTPException, http_exception_handler)  # type: ignore
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LimitUploadSize, max_upload_size=1024 * 1024 * 25)  # ~25MB

plugin_manager.load_plugins()

app.include_router(user_router)
app.include_router(comic_router)
