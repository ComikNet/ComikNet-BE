from fastapi import APIRouter, Response, Depends, HTTPException, Form, Request

from Models.user import User
from Models.requests import ComicSearchReq
from Models.response import ExceptionResponse, StandardResponse
from Services.Database.database import get_db
from Services.Limiter.limiter import limiter
from Services.Security.user import get_current_user
from Services.Modulator.manager import plugin_manager

comic_router = APIRouter(prefix="/comic")


@comic_router.post("/search")
async def search_comic(body: ComicSearchReq, user: User = Depends(get_current_user)):
    pass


@comic_router.get("/{src_id}/album/{album_id}")
async def get_album(src_id: str, album_id: str, user: User = Depends(get_current_user)):
    if (source := plugin_manager.get_source(src_id)) is None:
        raise ExceptionResponse.not_found


@comic_router.get("/{src_id}/album/{album_id}/images/{chapter_id}")
async def get_chapter_images(
    src_id: str, album_id: str, chapter_id: str, user: User = Depends(get_current_user)
):
    pass
