from fastapi import APIRouter, Response, Depends, HTTPException, Form, Request

from Models.user import User
from Services.Database.database import get_db
from Services.Limiter.limiter import limiter
from Services.Security.user import get_current_user
from Models.requests import ComicSearchReq

comic_router = APIRouter(prefix="/comic")


@comic_router.post("/search")
async def search_comic(body: ComicSearchReq, user: User = Depends(get_current_user)):
    pass


@comic_router.get("/{src_id}/album/{album_id}")
async def get_album(src_id: str, album_id: str, user: User = Depends(get_current_user)):
    pass


@comic_router.get("/{src_id}/album/{album_id}/images/{chapter_id}")
async def get_chapter_images(src_id: str, album_id: str, chapter_id: str, user: User = Depends(get_current_user)):
    pass
