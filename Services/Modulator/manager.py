import importlib
import json
import logging
import os
from http.cookies import BaseCookie
from pathlib import Path
from typing import Set

import toml

from Models.plugins import BasePlugin, Plugin
from Services.Config.config import config

logger = logging.getLogger(__name__)


class PluginManager:
    cnm_version = "0.3.1"

    def __init__(self):
        self.strict = config.plugin.strict_load
        self.plugins: Set[Plugin] = set()
        self.registered_source: Set[str] = set()

    def load_plugins(self) -> None:
        for plugin in os.listdir("Plugins"):
            if not plugin.startswith("_") and os.path.isdir(
                os.path.join("Plugins", plugin)
            ):
                if not self.load_plugin(
                    Path(os.path.join("Plugins", plugin)).resolve()
                ):
                    logger.error("An error occurred while loading plugins")
                    if self.strict:
                        raise RuntimeError("An error occurred while loading plugins")

    def load_plugin(self, plugin_dir: Path) -> bool:
        try:
            with open(
                plugin_dir.joinpath("pyproject.toml"), "r", encoding="utf-8"
            ) as f:
                plugin_info = toml.load(f)

            if (plugin_name := plugin_info["project"]["name"]) in self.plugins:
                logger.warning(f"Plugin {plugin_name} already loaded")
                return False

            src_list: list[str] = []
            for src in plugin_info["tool"]["cnm"]["source"]:
                if src in self.registered_source:
                    logger.error(
                        f"Failed to load {plugin_name}, source {plugin_info['plugin']['source']} has already been registered"
                    )
                    return False
                else:
                    logger.info(f"Registering source {src}")
                    src_list.append(src)

            module = importlib.import_module(f"Plugins.{plugin_dir.name}.main")

            if issubclass(entry := getattr(module, plugin_dir.name), BasePlugin):
                instance = entry()
                if instance.on_load():
                    self.plugins.add(
                        Plugin(
                            name=plugin_name,
                            version=plugin_info["project"]["version"],
                            cnm_version=plugin_info["plugin"]["cnm"]["version"],
                            source=plugin_info["plugin"]["cnm"]["source"],
                            service=plugin_info["cnm"]["service"],
                            instance=instance,
                        )
                    )
                else:
                    raise ImportError
                logger.info(f"Plugin {plugin_dir.name} Loaded")
                self.registered_source.update(src_list)
                return True
            else:
                logger.error(f"Plugin {plugin_dir.name} is not a valid plugin")
                return False
        except ModuleNotFoundError as module_err:
            logger.error(
                f"Failed to load {plugin_dir.name}, plugin requires some dependencies: {module_err.msg}"
            )
            return False
        except FileNotFoundError:
            logger.error(f"Failed to load plugin {plugin_dir.name}'s information")
            return False
        except ImportError:
            logger.error(f"Failed to import plugin {plugin_dir.name}'s main module")
            return False
        except KeyError:
            logger.error(f"Failed to load plugin {plugin_dir.name}'s information")
            return False
        except Exception as e:
            logger.error(
                f"Unknown error occurred while loading plugin {plugin_dir.name}"
            )
            logger.exception(e)
            return False

    def unload_plugin(self) -> None:
        while len(self.plugins) > 0:
            plugin = self.plugins.pop()
            plugin.instance.on_unload()
            logger.info(f"Plugin {plugin.name} unloaded")

    def get_source(self, source: str) -> Plugin | None:
        return next(
            (plugin for plugin in self.plugins if source in plugin.source), None
        )


class PluginUtils:
    @staticmethod
    def load_cookies(cookies_str: str | None) -> dict[str, BaseCookie[str]]:
        cookies = dict[str, BaseCookie[str]]()
        if cookies_str is None or cookies_str == "":
            return cookies

        try:
            plugin_cookies: dict[str, str] = json.loads(cookies_str)

            for src in plugin_manager.registered_source:
                if src in plugin_cookies:
                    cookies[src] = BaseCookie[str](plugin_cookies[src])
                else:
                    cookies[src] = BaseCookie[str]()
        except Exception:
            logger.warning("Failed to load cookies")

        return cookies


plugin_manager = PluginManager()
