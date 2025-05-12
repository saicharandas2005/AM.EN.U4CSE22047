import redis.asyncio as redis
from typing import Optional

class RedisCache:
    def __init__(self):
        self.client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

    async def get(self, key: str) -> Optional[str]:
        return await self.client.get(key)

    async def set(self, key: str, value: str, ttl: int = 300) -> None:
        await self.client.setex(key, ttl, value)

    async def close(self):
        await self.client.aclose()