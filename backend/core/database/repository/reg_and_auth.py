from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.core.constants import RoleName
from backend.core.database.models import User, Role
from backend.core.schemas.user import UserRegister


class RegisterRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def register_user(self, new_user: User) -> User:
        """
        Регистрирует пользователя после всех проверок

        Args:
            new_user - SQLAlchemy-модель пользователя для регистрации со всеми нужными полями

        Returns:
            Модель зарегистрированного пользователя
        """
        self.session.add(instance=new_user)
        await self.session.commit()
        await self.session.refresh(instance=new_user)

        return new_user

    async def check_user_exists(self, user_in: UserRegister) -> bool:
        """
        Проверяет по email, зарегистрирован ли пользователь
        Args:
            user_in - Pydantic-модель пользователя для регистрации

        Returns:
            True - если пользователь существует, False - если нет
        """
        stmt = select(User).where(User.email == user_in.email)
        result = await self.session.execute(statement=stmt)
        return result.scalar_one_or_none() is not None

    async def get_role_id(self, role_name: RoleName) -> int | None:
        """
        Получает ID роли по ее названию

        Args:
            role_name - название роли в формате StrEnum

        Returns:
            ID роли - если нашлась, None - если нет
        """
        stmt = select(Role).where(Role.name == role_name)
        result_role = await self.session.execute(statement=stmt)
        role_obj: Role | None = result_role.scalar_one_or_none()

        return role_obj.id if role_obj else None


class AuthRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user_and_role_by_user_id(self, user_id: int) -> User | None:
        """
        Получает модель пользователя по ID и его роль

        Args:
            user_id - ID пользователя

        Returns:
            Модель пользователя с загруженной ролью или None, если пользователь не найден
        """
        # selectinload для подгрузки роли, так как дальше будем к ней обращаться
        stmt = select(User).where(User.id == user_id).options(selectinload(User.role))
        result = await self.session.execute(statement=stmt)
        return result.scalar_one_or_none()

    async def get_user(self, email: str) -> User | None:
        """
        Получает модель пользователя по email

        Args:
            email - email пользователя

        Returns:
            Модель пользователя или None, если email не найден
        """
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(statement=stmt)
        return result.scalar_one_or_none()

    async def activate_user(self, user: User) -> User:
        """
        Активирует пользователя

        Args:
            user - модель существующего неактивного пользователя для активации

        Returns:
            Обновленная модель пользователя с is_active=True
        """
        user.is_active = True

        self.session.add(instance=user)
        await self.session.commit()
        await self.session.refresh(instance=user)

        return user
