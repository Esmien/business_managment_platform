from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.user.models import User
from backend.user.schemas import UserDTO
from tests.fixtures.environment_setup import fixture_async_session_maker


async def override_get_regular_user():
    """Вспомогательная функция для переключения на обычного пользователя без прав"""
    async with fixture_async_session_maker() as session:
        stmt = (
            select(User)
            .where(User.email == "user@user.com")
            .options(selectinload(User.role))
        )
        result = await session.execute(stmt)
        user_model = result.scalar_one_or_none()
        return UserDTO.model_validate(user_model) if user_model else None