from abc import ABC, abstractmethod

from Models.response import StandardResponse
from Models.comic import BaseComicInfo


class BasePlugin(ABC):
    @abstractmethod
    def on_load(self) -> bool:
        pass

    def on_unload(self) -> None:
        pass

    @abstractmethod
    def search(self, keyword: str) -> list[BaseComicInfo]:
        pass


class IAuth:
    @abstractmethod
    def login(self, body: dict[str, str]) -> StandardResponse:
        pass


class IShaper:
    @abstractmethod
    def imager_shaper(self):
        pass


class Plugin:
    name: str
    version: str
    cnm_version: str
    source: list[str]
    service: dict
    instance: BasePlugin

    def __init__(
        self,
        name: str,
        version: str,
        cnm_version: str,
        source: list[str],
        instance: BasePlugin,
    ):
        self.name = name
        self.version = version
        self.cnm_version = cnm_version
        self.source = source
        self.instance = instance
