from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database.models import User


class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def update_user(self, user: User, update_dict: dict[str, Any]) -> User:
        """
        Обновляет данные пользователя (имя, фамилия, отчество)

        Args:
            user - исходная модель пользователя
            update_dict - данные для обновления

        Returns:
            Обновленная модель пользователя
        """
        # Обновляет поля исходной модели User данными из update_dict
        for key, value in update_dict.items():
            setattr(user, key, value)

        self.session.add(instance=user)
        await self.session.commit()
        await self.session.refresh(instance=user)

        return user

    async def soft_delete_user(self, user: User) -> None:
        """
        Выполняет мягкое удаление пользователя (деактивацию)

        Args:
            user - модель пользователя для деактивации
        """
        user.is_active = False
        self.session.add(instance=user)
        await self.session.commit()
