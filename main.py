import logging

import fastapi
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rich.logging import RichHandler
from slowapi.errors import RateLimitExceeded

from Models.response import ExceptionResponse
from Routers.comic import comic_router
from Routers.user import user_router
from Services.Limiter.limiter import limiter
from Services.Modulator.manager import plugin_manager

logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, tracebacks_suppress=[fastapi])],
)

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, ExceptionResponse.limit_exceeded)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

plugin_manager.load_plugins()

app.include_router(user_router)
app.include_router(comic_router)
