import asyncio
import inspect
from abc import ABC, abstractmethod
from typing import Any

import nest_asyncio

from Models.comic import BaseComicInfo, ComicInfo
from Models.response import StandardResponse
from Models.user import UserData

nest_asyncio.apply()


class BasePlugin(ABC):
    @abstractmethod
    def on_load(self) -> bool:
        pass

    @abstractmethod
    def on_unload(self) -> None:
        pass

    @abstractmethod
    def search(self, keyword: str, **kwargs) -> list[BaseComicInfo]:
        pass

    @abstractmethod
    def album(self, album_id: str, **kwargs) -> ComicInfo:
        pass


class IAuth(ABC):
    auto_login: bool

    @abstractmethod
    async def login(
        self, body: dict[str, str], user_data: UserData
    ) -> StandardResponse:
        pass


class IShaper(ABC):
    @abstractmethod
    def imager_shaper(self):
        pass


class Plugin:
    name: str
    version: str
    cnm_version: str
    source: list[str]
    service: dict[str, list[str]]
    instance: BasePlugin

    def __init__(
        self,
        name: str,
        version: str,
        cnm_version: str,
        source: list[str],
        service: dict[str, list[str]],
        instance: BasePlugin,
    ):
        self.name = name
        self.version = version
        self.cnm_version = cnm_version
        self.source = source
        self.service = service
        self.instance = instance

    def try_call(self, method: str, *args: Any, **kwargs: Any) -> Any:
        if hasattr(self.instance, method):
            if inspect.iscoroutinefunction(getattr(self.instance, method)):
                loop = asyncio.get_event_loop()
                return loop.run_until_complete(
                    getattr(self.instance, method)(*args, **kwargs)
                )
            else:
                return getattr(self.instance, method)(*args, **kwargs)
        else:
            return None
