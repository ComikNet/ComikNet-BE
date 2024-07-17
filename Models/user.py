import json
from datetime import datetime
from http.cookies import BaseCookie

from pydantic import BaseModel


class User(BaseModel):
    uid: str
    email: str
    username: str
    created_at: datetime


class UserData:
    uid: str
    plugin_cookies: dict[str, BaseCookie[str]]

    def __init__(self, uid: str, plugin_cookies: dict[str, BaseCookie[str]]):
        self.uid = uid
        self.plugin_cookies = plugin_cookies

    def get_src_cookies(self, src: str) -> BaseCookie[str]:
        if src in self.plugin_cookies:
            return self.plugin_cookies[src]
        else:
            return BaseCookie[str]()

    def __str__(self):
        return json.dumps(
            {k: v.output(header="").strip() for k, v in self.plugin_cookies.items()}
        )


class Token(BaseModel):
    access_token: str
    token_type: str
