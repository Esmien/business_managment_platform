from loguru import logger

from backend.core.constants import RoleName
from backend.core.database.models.users import User
from backend.core.database.repository.reg_and_auth import (
    AuthRepository,
    RegisterRepository,
)
from backend.core.schemas.user import Token, UserRegister
from backend.exceptions import (
    UserExistsError,
    UserNotActiveError,
    UserDoesNotExistsError,
    RoleDoesNotExistsError,
    UserAlreadyActiveError,
)
from backend.core.security import (
    verify_password,
    create_access_token,
    get_password_hash,
)


class RegisterService:
    def __init__(self, repo: RegisterRepository):
        self.repo = repo

    async def register_user(
        self, user_in: UserRegister, role_name: RoleName = RoleName.USER
    ) -> User:
        """
        Регистрирует пользователя, присваивая ему роль

        Args:
            user_in - Pydantic-модель пользователя с данными для регистрации
            role_name - присваиваемая роль (по умолчанию User)

        Returns:
            Модель зарегистрированного пользователя

        Raises:
            UserExistsError - если пользователь существует
            RoleDoesNotExistsError - присваиваемая роль не найдена
        """
        # Проверка на существование пользователя с переданным email
        is_user_exists = await self.repo.check_user_exists(user_in=user_in)

        if is_user_exists:
            raise UserExistsError

        # Защита от присвоения несуществующей роли
        role_id = await self.repo.get_role_id(role_name=role_name)

        # Проблема на стороне сервера, роль не найдена
        if not role_id:
            raise RoleDoesNotExistsError

        # Собираем модель пользователя со всеми полями
        new_user = User(
            email=str(user_in.email),
            hashed_password=await get_password_hash(user_in.password),
            name=user_in.name,
            surname=user_in.surname,
            last_name=user_in.last_name,
            role_id=role_id,
            is_active=True,
        )

        # Регистрируем
        return await self.repo.register_user(new_user)


class AuthService:
    def __init__(self, repo: AuthRepository):
        self.repo = repo

    @staticmethod
    def _check_user_active(user: User) -> bool:
        """Возвращает True если пользователь активен (is_active=True)"""
        return user.is_active

    async def check_users_creds(self, email: str, password: str) -> User:
        """
        Проверка учетных данных пользователя.
        Используется при аутентификации и восстановлении пользователя

        Args:
            email - Электронная почта пользователя
            password - Пароль пользователя

        Raises:
            UserDoesNotExistsError - если пользователь с этим email не найден
            InvalidPasswordError - если пароль неверный (приходит от verify_password)

        Returns:
            Объект пользователя, если учетные данные верны
        """
        user = await self.repo.get_user(email=email)

        if not user:
            raise UserDoesNotExistsError

        await verify_password(
            plain_password=password, hashed_password=user.hashed_password
        )

        return user

    async def activate_user(self, user: User) -> User:
        """
        Активирует аккаунт пользователя

        Args:
            user - модель пользователя

        Returns:
            Модель пользователя с is_active=True

        Raises:
            UserAlreadyActiveError - если пользователь активен
        """
        if self._check_user_active(user=user):
            logger.warning(f"Пользователь {user.name} уже активен")
            raise UserAlreadyActiveError

        return await self.repo.activate_user(user=user)

    async def get_auth_token(self, user: User) -> Token:
        """
        Получает сырой JWT-токен для пользователя

        Args:
            user - запрашивающий токен пользователь

        Returns:
            Token(access_token=JWT-строка, token_type="bearer")

        Raises:
            UserNotActiveError - если запрашивающий юзер неактивен
        """
        # Если пользователь неактивен, токен ему не положен
        if not self._check_user_active(user=user):
            logger.warning(f"Пользователь {user.name} не активен")
            raise UserNotActiveError

        # Генерируем токен
        access_token = create_access_token(data={"sub": str(user.id)})

        return Token(access_token=access_token, token_type="bearer")

    async def get_active_user_by_id(self, user_id: int) -> User:
        """
        Получает активного пользователя по ID

        Args:
            user_id - искомый ID

        Returns:
            Модель найденного пользователя

        Raises:
            UserDoesNotExistsError - если пользователь не найден
            UserNotActiveError - если найден, но неактивен
        """
        user = await self.repo.get_user_and_role_by_user_id(user_id)

        if not user:
            raise UserDoesNotExistsError
        if not self._check_user_active(user):
            raise UserNotActiveError

        return user
