import json
from datetime import datetime

from pydantic import BaseModel


class User(BaseModel):
    user_id: str
    email: str
    username: str
    created_at: datetime


class UserData:
    uid: str
    plugin_cookies: dict[str, dict[str, str]] | None

    def __init__(
        self, uid: str, plugin_cookies: dict[str, dict[str, str]] | None = None
    ) -> None:
        self.uid = uid
        self.plugin_cookies = plugin_cookies

    def set_src_cookies(self, src: str, cookies: dict[str, str | None]) -> None:
        if self.plugin_cookies is None:
            self.plugin_cookies = dict()
        _cookies = {k: v for k, v in cookies.items() if v is not None}
        self.plugin_cookies[src] = _cookies

    def get_src_cookies(self, src: str) -> dict[str, str]:
        return self.plugin_cookies.get(src, dict()) if self.plugin_cookies else dict()

    def __str__(self):
        return (
            json.dumps(self.plugin_cookies, ensure_ascii=False)
            if self.plugin_cookies
            else "{}"
        )


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    sub: str
    id: str
    exp: datetime | None = None
