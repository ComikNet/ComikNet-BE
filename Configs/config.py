import json


class Config:
    def __init__(self, config_path: str):
        with open(config_path, "r", encoding="utf-8") as f:
            self.config: dict = json.load(f)

    def get_config(self, *keys) -> object | None:
        keys = [*keys]
        result: object | None = self.config
        while len(keys) > 0:
            key = keys.pop(0)
            if (isinstance(result, list) and key < len(result)) or (
                isinstance(result, dict) and key in result.keys()
            ):
                result = result[key]
            else:
                return None
        return result


config = Config("Configs/config.json")
