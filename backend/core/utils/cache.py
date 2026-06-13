from collections.abc import Callable
from functools import wraps
from typing import Any

from backend.rbac.schemas import AccessRuleDTO


def rbac_cache(ttl: int = 3600) -> Callable:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(
            self: Any, role_id: int, business_element_name: str
        ) -> AccessRuleDTO | None:
            # Формируем ключ напрямую из аргументов
            cache_key = f"rbac:rule:{role_id}:{business_element_name}"

            # Проверяем кэш
            cached_data = await self.redis.get(cache_key)
            if cached_data:
                return AccessRuleDTO.model_validate_json(cached_data)

            # Вызываем оригинальный метод, если был промах
            result = await func(self, role_id, business_element_name)

            # Кэшируем результат
            if result:
                await self.redis.setex(
                    name=cache_key, time=ttl, value=result.model_dump_json()
                )
            return result

        return wrapper

    return decorator
