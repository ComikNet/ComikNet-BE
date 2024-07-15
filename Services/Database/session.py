import redis.asyncio as redis

from Configs.config import config


class UserSession:
    def __init__(self):
        protocol = config.get_config("redis", "protocol")
        host = config.get_config("redis", "host")
        port = config.get_config("redis", "port")
        username = config.get_config("redis", "username")
        password = config.get_config("redis", "password")
        auth = f"{username}:{password}@" if username and password else ""

        if not host or not port:
            raise ValueError("Please complete the redis configuration")

        self.client = redis.from_url(f"{protocol}://{auth}{host}:{port}")

    """ async def save_src_token(
        self, src: str, user: str, cookies: dict[str, str]
    ) -> None:
        await self.client.hmset(f"token:{user}:{src}", cookies)

    async def get_src_token(self, src: str, user: str) -> dict[str, str] | None:
        return await self.client.hgetall(f"token:{user}:{src}") """
