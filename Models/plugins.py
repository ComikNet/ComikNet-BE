from abc import ABC, abstractmethod


class BasePlugin(ABC):
    @abstractmethod
    def on_load(self) -> bool:
        pass

    def on_unload(self) -> None:
        pass


class Plugin:
    name: str
    version: str
    cnm_version: str
    source: list[str]
    instance: BasePlugin

    def __init__(self, name: str, version: str, cnm_version: str, source: list[str], instance: BasePlugin):
        self.name = name
        self.version = version
        self.cnm_version = cnm_version
        self.source = source
        self.instance = instance
