from pydantic import BaseModel

from typing import List, Optional, Dict, Any


class BaseComicInfo(BaseModel):
    """BaseComicInfo"""
    """作者，漫画作者"""
    author: List[str]
    """封面，漫画封面图片URL"""
    cover: str
    """标识符，漫画在所属平台的索引ID"""
    id: str
    """名称，漫画名称"""
    name: str


class ComicInfo(BaseModel):
    """ComicInfo"""
    """章节数，漫画章节数"""
    chapters: Optional[int] = None
    """评论量，漫画评论量"""
    comments: Optional[int] = None
    """简介，漫画简介"""
    description: Optional[str] = None
    """额外信息，源平台携带的其它漫画信息"""
    extras: Optional[Dict[str, Any]] = None
    """收藏量，漫画收藏量"""
    favorites: Optional[int] = None
    """已收藏，漫画是否已收藏"""
    is_favorite: Optional[bool] = None
    """已完结，漫画是否已完结"""
    is_finished: Optional[bool] = None
    """已阅读，漫画是否已阅读"""
    is_viewed: Optional[bool] = None
    """标签，漫画标签"""
    tags: Optional[List[str]] = None
    """更新时间，漫画最近的更新时间戳"""
    updated_at: Optional[int] = None
    """阅读量，漫画阅读量"""
    views: Optional[int] = None
