import importlib
import json
import logging
import os
from http.cookies import BaseCookie
from pathlib import Path
from typing import Set, cast

import toml
from fastapi import Response

from Configs.config import config
from Models.plugins import BasePlugin, Plugin

logger = logging.getLogger(__name__)


class PluginManager:
    def __init__(self):
        if strict := config.get_config("plugin", "strict_load") is None:
            self.strict = False
        else:
            self.strict = strict
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
        if plugin_dir.name in self.plugins:
            logger.warning(f"Plugin {plugin_dir.name} already loaded")
            return False

        try:
            with open(
                plugin_dir.joinpath(f"{plugin_dir.name}.toml"), "r", encoding="utf-8"
            ) as f:
                plugin_info = toml.load(f)

            for src in plugin_info["plugin"]["source"]:
                if src in self.registered_source:
                    logger.error(
                        f"Failed to load {plugin_dir.name}, {plugin_info['plugin']['source']} has already been registered"
                    )
                    return False
                else:
                    logger.info(f"Registering source {src}")

                module = importlib.import_module(f"Plugins.{plugin_dir.name}.main")
            if issubclass(entry := getattr(module, plugin_dir.name), BasePlugin):
                instance = entry()
                if instance.on_load():
                    self.plugins.add(
                        Plugin(
                            name=plugin_info["description"]["name"],
                            version=plugin_info["description"]["version"],
                            cnm_version=plugin_info["plugin"]["cnm-version"],
                            source=plugin_info["plugin"]["source"],
                            service=plugin_info["service"],
                            instance=instance,
                        )
                    )
                else:
                    raise ImportError
                logger.info(f"Plugin {plugin_dir.name} Loaded")
                self.registered_source.add(src)
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
        except:
            logger.error(
                f"Unknown error occurred while loading plugin {plugin_dir.name}"
            )
            return False

    def unload_plugin(self) -> None:
        while len(self.plugins) > 0:
            plugin = self.plugins.pop()
            plugin.instance.on_unload()
            logger.info(f"Unloaded plugin {plugin.name}")

    def get_source(self, source: str) -> Plugin | None:
        if source in self.registered_source:
            for plugin in self.plugins:
                if source in plugin.source:
                    return plugin
        else:
            return None


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
        except:
            logger.warning("Failed to load cookies")

        return cookies


plugin_manager = PluginManager()
