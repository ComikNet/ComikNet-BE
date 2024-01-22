from pydantic import BaseModel


class SourceStorageReq(BaseModel):
    account: str
    src_pwd: str
    key_pwd: str
