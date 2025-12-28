from logging import getLogger
from typing import Any

import msgspec
from redis.asyncio import Redis

from src.application.ports.session_storage import SessionStorage
from src.infrastructure.constants import TTL_FOR_STORAGE
from src.infrastructure.exceptions.storage_exceptions import StorageError

logger = getLogger(__name__)


class RedisStorage(SessionStorage):
    def __init__(self, redis_client: Redis) -> None:
        self.client = redis_client
        self.ttl = TTL_FOR_STORAGE
        self.encoder = msgspec.json.Encoder()
        self.decoder = msgspec.json.Decoder()

    async def get(self, key: str) -> dict[str, Any] | None:
        try:
            data = await self.client.get(key)
            if data is None:
                return None

            decoded: dict[str, Any] = self.decoder.decode(data)
            return decoded

        except msgspec.DecodeError as e:
            logger.error(f"Invalid data for key {key}: {str(e)}")
            raise StorageError(f"Invalid data format: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to get data for key {key}: {str(e)}")
            raise StorageError(f"Failed to get data: {str(e)}")

    async def set(self, key: str, value: dict[str, Any], ttl: int | None = None) -> None:
        try:
            serialized = self.encoder.encode(value)
            await self.client.set(key, serialized, ex=ttl if ttl else self.ttl)

        except msgspec.EncodeError as e:
            logger.error(f"Failed to encode data for key {key}: {str(e)}")
            raise StorageError(f"Failed to encode data: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to set data for key {key}: {str(e)}")
            raise StorageError(f"Failed to set data: {str(e)}")

    async def update(self, key: str, value: dict[str, Any], ttl: int | None = None) -> None:
        try:
            current = await self.get(key)

            if not current:
                await self.set(key, value, ttl)
                return

            current.update(value)
            await self.set(key, current, ttl)

        except Exception as e:
            logger.error(f"Failed to update data for key {key}: {str(e)}")
            raise StorageError(f"Failed to update data: {str(e)}")

    async def delete(self, key: str) -> None:
        try:
            await self.client.delete(key)
        except Exception as e:
            logger.error(f"Failed to delete data for key {key}: {str(e)}")
            raise StorageError(f"Failed to delete session: {str(e)}")
