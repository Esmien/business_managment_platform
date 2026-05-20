from backend.core.database.models import User
from backend.core.database.repository.user import UserRepository
from backend.core.schemas.user import UserUpdate


class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    async def update_profile(self, user: User, update_data: UserUpdate) -> User:
        """
        Обновляет данные пользователя (ФИО)

        Args:
            user - модель пользователя для обновления
            update_data - данные, которые пользователь хочет обновить

        Returns:
            Обновленная модель пользователя (или исходная, если данных для обновления нет)
        """
        # Сериализуем данные для дальнейшей обработки в репозитории, исключая не заданные поля
        update_dict = update_data.model_dump(exclude_unset=True)

        if not update_dict:
            return user

        return await self.repo.update_user(user=user, update_dict=update_dict)

    async def soft_delete_profile(self, user: User) -> None:
        """Мягко удаляет пользователя (деактивирует)"""
        await self.repo.soft_delete_user(user=user)
