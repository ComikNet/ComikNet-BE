import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from rich.logging import RichHandler
from slowapi.errors import RateLimitExceeded

from Routers.user import user_router
from Models.response import ExceptionResponse
from Services.Limiter.limiter import limiter

logging.basicConfig(level="INFO", format="%(message)s", datefmt="[%X]", handlers=[RichHandler()])

app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, ExceptionResponse.limit_exceeded)  # type: ignore
app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
