import asyncio
import os
import json
import gzip
from typing import Any, Optional

from pydantic import BaseModel
from redis.asyncio import Redis
from Services.logger_service import LoggerService


class RedisService:
    _instance = None
    _lock = asyncio.Lock()

    def __init__(self):
        self.redis = None
        self.logger = LoggerService("prediction_service").get_logger()

    @classmethod
    async def get_instance(cls):
        if cls._instance is None:
            async with cls._lock:
                if cls._instance is None:
                    instance = cls()
                    await instance.setup()
                    cls._instance = instance
        return cls._instance

    async def setup(self):
        redis_url = os.getenv("REDIS_URL")
        if not redis_url:
            raise ValueError("REDIS_URL not set in environment.")
        self.redis = Redis.from_url(redis_url)

    async def write_to_cache(self, key: str, value: dict, *, compress: bool = False, ex: int | None = None):
        if not isinstance(value, dict):
            raise TypeError(f"Expected dict, got {type(value).__name__}")

        try:
            serialized = json.dumps(value).encode("utf-8")
            data = gzip.compress(serialized) if compress else serialized

            if ex:
                await self.redis.setex(key, ex, data)
            else:
                await self.redis.set(key, data)

            self.logger.info(f"Cache write successful for key: {key}")
        except Exception as e:
            self.logger.error(f"Failed to write to cache ({key}): {e}")
            raise

    async def read_from_cache(self, key: str, *, compressed: bool = False):
        try:
            data = await self.redis.get(key)
            if data is None:
                self.logger.info(f"Cache miss for key: {key}")
                return None

            if compressed:
                data = gzip.decompress(data)

            return json.loads(data.decode("utf-8"))
        except Exception as e:
            self.logger.error(f"Failed to read from cache ({key}): {e}")
            raise

    async def delete(self, key: str):
        try:
            await self.redis.delete(key)
            self.logger.info(f"Deleted key from cache: {key}")
        except Exception as e:
            self.logger.error(f"Failed to delete key ({key}): {e}")
            raise

    async def close(self):
        if self.redis:
            await self.redis.close()
            self.logger.info("🔌 Redis connection closed.")