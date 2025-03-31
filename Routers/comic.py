from fastapi import APIRouter, Depends, HTTPException

from Models.comic import BaseComicInfo, ComicInfo
from Models.requests import ComicSearchReq
from Models.response import BaseResponse, StandardResponse
from Models.user import User, UserData
from Services.Modulator.manager import plugin_manager
from Services.Security.user import get_current_user, get_user_data

comic_router = APIRouter(prefix="/comic")


@comic_router.post("/search", response_model=BaseResponse[list[BaseComicInfo]])
async def search_comic(
    body: ComicSearchReq, user: User = Depends(get_current_user)
) -> StandardResponse[list[BaseComicInfo]]:
    # TODO: Performence imporvement
    result = []
    for source in plugin_manager.plugins:
        resp = source.instance.search(body.keyword, *body.extras)

        result.extend(resp)

    return StandardResponse[list[BaseComicInfo]](data=result)


@comic_router.get("/{src_id}/album/{album_id}", response_model=BaseResponse[ComicInfo])
async def get_album(src_id: str, album_id: str) -> StandardResponse[ComicInfo]:
    if (source := plugin_manager.get_source(src_id)) is None:
        raise HTTPException(status_code=404, detail="Source not found")

    return StandardResponse[ComicInfo](data=source.instance.album(album_id))


@comic_router.get("/{src_id}/favor", response_model=BaseResponse[list[BaseComicInfo]])
async def get_favor(
    src_id: str,
    data: dict[str, str] | None = None,
    user_data: UserData = Depends(get_user_data),
) -> StandardResponse[list[BaseComicInfo]]:
    if (source := plugin_manager.get_source(src_id)) is None:
        raise HTTPException(status_code=404, detail="Source not found")

    if (resp := source.try_call("get_favor", user_data, data)) is not None:
        return resp

    return StandardResponse(status_code=400, message="Source not support")


@comic_router.get("/{src_id}/album/{album_id}/images/{chapter_id}")
async def get_chapter_images(
    src_id: str, album_id: str, chapter_id: str, user: User = Depends(get_current_user)
):
    if (source := plugin_manager.get_source(src_id)) is None:
        raise HTTPException(status_code=404, detail="Source not found")

    pass
