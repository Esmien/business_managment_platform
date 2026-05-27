from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from backend.core.config import settings
from backend.core.constants import BusinessElementName, PermissionName
from backend.exceptions import UserDoesNotExistsError, UserNotActiveError

from backend.api.dependencies.reg_and_auth import AuthServiceDepends
from backend.api.dependencies.rbac import RbacServiceDepends
from backend.user.schemas import UserDTO

# Извлекает Bearer-токен из заголовка Authorization
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    auth_service: AuthServiceDepends,
    token: str = Depends(oauth2_scheme),
) -> UserDTO:
    """
    Возвращает текущего активного пользователя по JWT токену

    Args:
        token - JWT токен пользователя
        auth_service - сервисный модуль для работы с аутентификацией

    Returns:
        Модель текущего авторизованного пользователя

    Raises:
        HTTPException(401) - при невалидном JWT
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Ошибка валидации токена",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Декодируем токен и проверяем его валидность и вытаскиваем id пользователя
    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.security.SECRET_KEY,
            algorithms=[settings.security.ALGORITHM],
        )
        user_id = payload.get("sub")

        if user_id is None:
            raise credentials_exception
    except jwt.InvalidTokenError:
        raise credentials_exception

    # Проверяем, активен ли пользователь (is_active=True)
    try:
        user = await auth_service.get_active_user_by_id(user_id=int(user_id))
        return user
    except (UserDoesNotExistsError, UserNotActiveError):
        raise credentials_exception


class PermissionChecker:
    """Динамический чекер прав доступа через RBAC"""

    def __init__(
        self, business_element: BusinessElementName, permission: PermissionName
    ):
        """
        Инициализация чекера

        Args:
            business_element - ресурс, к которому проверяется доступ
            permission - тип прав доступа (read, create, delete и т.д.)
        """
        self.business_element = business_element
        self.permission = permission

    async def __call__(
        self,
        user: "CurrentUserDepends",
        rbac_service: RbacServiceDepends,
    ) -> UserDTO:
        """
        Делает класс вызываемым.
        Выполняет проверку прав доступа к ресурсу

        Args:
            user - текущий пользователь
            rbac_service - сервис проверки прав

        Returns:
            Возвращает модель пользователя, если прошел проверку

        Raises:
            HTTPException(403) - если не достаточно прав для доступа к ресурсам
        """
        # Проверка прав доступа для роли пользователя к ресурсу
        has_access = await rbac_service.check_permission(
            role_id=user.role_id,
            element_name=self.business_element,
            permission=self.permission,
        )

        # Доступа нет
        if not has_access:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="У вас нет прав на выполнение этого действия",
            )

        return user


CurrentUserDepends = Annotated[UserDTO, Depends(get_current_user)]
