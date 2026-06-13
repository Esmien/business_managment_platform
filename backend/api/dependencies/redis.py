from typing import Annotated

from fastapi import Depends
from redis.asyncio import Redis

from backend.core.database.redis import redis_client


def get_redis() -> Redis:
    """Провайдер для Dependency Injection в FastAPI"""
    if redis_client is None:
        raise RuntimeError("Клиент Redis не инициализирован")
    return redis_client


RedisDepends = Annotated[Redis, Depends(get_redis)]
