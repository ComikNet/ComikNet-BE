import json
from typing import Any


class Config:
    def __init__(self, config_path: str):
        with open(config_path, "r") as f:
            self.config = json.load(f)

    def get_db_config(self, key: str) -> Any | None:
        try:
            return self.config["database"][key]
        except:
            return None


config = Config("Configs/config.json")
