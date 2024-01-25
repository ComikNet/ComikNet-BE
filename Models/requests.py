from pydantic import BaseModel


class SourceStorageReq(BaseModel):
    account: str
    src_pwd: str
    key_pwd: str


class SourceLoginReq(BaseModel):
    account: str
    password: str
    extra_info: dict[str, str] | None = None


class ComicSearchReq(BaseModel):
    sources: list[str]
    keyword: str
