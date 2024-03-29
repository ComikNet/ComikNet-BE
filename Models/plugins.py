from abc import ABC, abstractmethod

from Models.response import StandardResponse


class BasePlugin(ABC):
    @abstractmethod
    def on_load(self) -> bool:
        pass

    def on_unload(self) -> None:
        pass

    def login(self, username: str, password: str) -> StandardResponse:
        pass


class Plugin:
    name: str
    version: str
    cnm_version: str
    source: list[str]
    service: dict
    instance: BasePlugin

    def __init__(self, name: str, version: str, cnm_version: str, source: list[str], service: dict,
                 instance: BasePlugin):
        self.name = name
        self.version = version
        self.cnm_version = cnm_version
        self.source = source
        self.service = service
        self.instance = instance
