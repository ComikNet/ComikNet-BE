import importlib
import json
import os
from pathlib import Path
from typing import Set
import logging

import toml
from packaging.version import Version, parse

from Models.plugins import BasePlugin, Plugin
from Services.Config.config import config

logger = logging.getLogger("[CNM]")


class PluginManager:
    cnm_version = Version("0.3.1")

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
                    logger.error("An error occurred while loading plugin")
                    if self.strict:
                        logger.error(
                            f"According to **STRICT** mode, server will abort if plugin {plugin} fails to load"
                        )
                        raise RuntimeError("An error occurred while loading plugins")

    def load_plugin(self, plugin_dir: Path) -> bool:
        logger.info(f"Loading plugin {plugin_dir.name}")
        try:
            with open(
                plugin_dir.joinpath("pyproject.toml"), "r", encoding="utf-8"
            ) as f:
                plugin_info = toml.load(f)

            if (plugin_name := plugin_info["project"]["name"]) in self.plugins:
                logger.warning(f"Plugin {plugin_name} already loaded")
                return False

            version = parse(plugin_info["tool"]["cnm"]["version"])
            if (
                self.cnm_version.major != version.major
                or self.cnm_version.minor != version.minor
            ):
                logger.error(
                    f"Plugin {plugin_name}'s CNM version {version} is not compatible with server's CNM version {self.cnm_version}"
                )
                return False

            src_list: list[str] = []
            for src in plugin_info["tool"]["cnm"]["source"]:
                if len(src) > 10:
                    logger.error(
                        f"Failed to load {plugin_name}, source id {src} is too long"
                    )
                    return False
                if src in self.registered_source:
                    logger.error(
                        f"Failed to load {plugin_name}, source {plugin_info['plugin']['source']} has already been registered"
                    )
                    return False
                else:
                    logger.info(f"Registering source {src}...")
                    src_list.append(src)

            module = importlib.import_module(f"Plugins.{plugin_dir.name}.main")

            if issubclass(entry := getattr(module, plugin_dir.name), BasePlugin):
                instance = entry()
                if instance.on_load():
                    self.plugins.add(
                        Plugin(
                            name=plugin_name,
                            version=plugin_info["project"]["version"],
                            cnm_version=plugin_info["tool"]["cnm"]["version"],
                            source=plugin_info["tool"]["cnm"]["source"],
                            service=plugin_info["tool"]["cnm"]["service"],
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
                f" Failed to load {plugin_dir.name}, plugin requires some dependencies: {module_err.msg}"
            )
            return False
        except FileNotFoundError:
            logger.error(f"Failed to load plugin {plugin_dir.name}'s information")
            return False
        except ImportError:
            logger.error(
                f"Failed to import plugin {plugin_dir.name}'s main module"
            )
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

    def unload_plugins(self) -> None:
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
    def load_cookies(cookies_str: str | None) -> dict[str, dict[str, str]]:
        if not cookies_str:
            return {}

        try:
            plugin_cookies = json.loads(cookies_str)
            if not isinstance(plugin_cookies, dict):
                raise ValueError("Invalid cookies format")

            return {
                src: plugin_cookies.get(src, {})
                for src in plugin_manager.registered_source
            }
        except (json.JSONDecodeError, ValueError) as e:
            logger.warning(f"Failed to load cookies: {e}")
        except Exception as e:
            logger.exception(
                "Unexpected error occurred while loading cookies", exc_info=e
            )

        return {}


plugin_manager = PluginManager()
