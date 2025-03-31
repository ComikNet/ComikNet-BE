import logging
from contextlib import asynccontextmanager

import fastapi
import uvicorn
from concurrent_log_handler import ConcurrentTimedRotatingFileHandler
from fastapi import FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from rich.logging import RichHandler
from slowapi.errors import RateLimitExceeded

from Models.response import http_exception_handler, validation_exception_handler
from Routers.comic import comic_router
from Routers.user import user_router
from Services.Config.config import config
from Services.Database.database import Base, engine
from Services.Limiter.limiter import (
    LimitUploadSize,
    RateLimitExceeded_handler,
    freq_limiter,
)
from Services.Modulator.manager import plugin_manager

logging.basicConfig(
    level=config.log.log_level,
    format="%(asctime)s - %(name)s [%(levelname)s] : %(message)s",
    datefmt="[%X]",
    handlers=[
        RichHandler(rich_tracebacks=True, tracebacks_suppress=[fastapi]),
        ConcurrentTimedRotatingFileHandler(
            "Logs/latest.log", when="midnight", interval=1
        ),
    ],
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine, checkfirst=True)
    plugin_manager.load_plugins()
    yield
    plugin_manager.unload_plugins()


app = FastAPI(lifespan=lifespan)


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

app.include_router(user_router)
app.include_router(comic_router)

if __name__ == "__main__":
    uvicorn.run(app, log_level="trace")
