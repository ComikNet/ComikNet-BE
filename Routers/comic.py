from fastapi import APIRouter, Depends, HTTPException

from Models.requests import ComicSearchReq
from Models.response import StandardResponse
from Models.user import User, UserData
from Services.Modulator.manager import plugin_manager
from Services.Security.user import get_current_user, get_user_data

comic_router = APIRouter(prefix="/comic")


@comic_router.post("/search")
async def search_comic(body: ComicSearchReq, user: User = Depends(get_current_user)):
    pass


@comic_router.get("/{src_id}/favor")
async def get_favor(
    src_id: str,
    data: dict[str, str] | None = None,
    user_data: UserData = Depends(get_user_data),
):
    if (source := plugin_manager.get_source(src_id)) is None:
        raise HTTPException(status_code=404, detail="Source not found")

    if (resp := source.try_call("get_favor", user_data, data)) is not None:
        return resp

    return StandardResponse(status_code=404, message="Not Found")


@comic_router.get("/{src_id}/album/{album_id}")
async def get_album(src_id: str, album_id: str, user: User = Depends(get_current_user)):
    if (source := plugin_manager.get_source(src_id)) is None:
        raise HTTPException(status_code=404, detail="Source not found")

    pass


@comic_router.get("/{src_id}/album/{album_id}/images/{chapter_id}")
async def get_chapter_images(
    src_id: str, album_id: str, chapter_id: str, user: User = Depends(get_current_user)
):
    if (source := plugin_manager.get_source(src_id)) is None:
        raise HTTPException(status_code=404, detail="Source not found")

    pass
