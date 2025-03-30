from pydantic import BaseModel


class SourceStorageReq(BaseModel):
    password: str
    data: dict[str, str]


class ComicSearchReq(BaseModel):
    sources: list[str]
    keyword: str
