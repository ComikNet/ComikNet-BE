import json
import os
from pathlib import Path

import toml
from pydantic import BaseModel


class SecurityConfig(BaseModel):
    secret_key: str


class DatabaseConfig(BaseModel):
    host: str
    port: int
    name: str
    username: str
    password: str


class EmailConfig(BaseModel):
    host: str
    port: int
    address: str
    password: str


class PluginConfig(BaseModel):
    strict_load: bool


class LogConfig(BaseModel):
    log_level: str


class Config(BaseModel):
    security: SecurityConfig
    database: DatabaseConfig
    email: EmailConfig
    plugin: PluginConfig
    log: LogConfig = LogConfig(log_level="INFO")

    @classmethod
    def load(cls):
        config_path = Path(
            os.path.join(os.getcwd()), "Services", "Config", "config.toml"
        )

        if not config_path.exists():
            return cls.load_json()

        _config = toml.load(config_path)
        return cls.model_validate(_config)

    @classmethod
    def load_json(cls):
        config_path = Path(
            os.path.join(os.getcwd()), "Services", "Config", "config.json"
        )

        if not config_path.exists():
            raise FileNotFoundError("Config file not found.")

        with open(config_path, "r", encoding="utf-8") as f:
            _config = json.load(f)
        return cls.model_validate(_config)


config = Config.load()
