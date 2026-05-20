from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.core.database.models import User
from backend.core.database.models.teams import Team
from backend.core.schemas.team import TeamCreate


class TeamRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_team_by_id(self, team_id: int) -> Team | None:
        """
        Получает модель команды по ее ID

        Args:
            team_id - ID команды

        Returns:
            Модель команды с загруженными участниками или None, если не найдена
        """
        stmt = (
            select(Team).where(Team.id == team_id).options(selectinload(Team.members))
        )
        result = await self.session.execute(statement=stmt)
        return result.scalar_one_or_none()

    async def check_team_name_exists(self, team_name: str) -> bool:
        """
        Проверяет, существует ли команда по ее названию

        Args:
            team_name - название команды

        Returns:
            True - если существует, False - если нет
        """
        stmt = select(Team).where(Team.name == team_name)
        result = await self.session.execute(statement=stmt)
        return result.scalar_one_or_none() is not None

    async def check_invite_code_exists(self, code: str) -> bool:
        """
        Проверяет, существует ли переданный инвайт-код у какой-либо команды.
        Необходимо для защиты от одинаковых кодов у разных команд

        Args:
            code - код для проверки

        Returns:
            True - если существует, False - если нет
        """
        stmt = select(Team).where(Team.invite_code == code)
        result = await self.session.execute(statement=stmt)
        return result.scalar_one_or_none() is not None

    async def get_team_by_invite_code(self, code: str) -> Team | None:
        """
        Находит команду по инвайт коду

        Args:
            code - инвайт код

        Returns:
            Модель соответствующей команды или None, если код неправильный
        """
        stmt = select(Team).where(Team.invite_code == code)
        result = await self.session.execute(statement=stmt)
        return result.scalar_one_or_none()

    async def create_team(self, team_in: TeamCreate, invite_code: str) -> Team:
        """
        Создает команду

        Args:
            team_in - Pydantic-модель команды для создания
            invite_code - сгенерированный инвайт-код для присвоения его команде

        Returns:
            Модель команды со всеми необходимыми полями
        """
        new_team = Team(
            name=team_in.name, description=team_in.description, invite_code=invite_code
        )

        self.session.add(instance=new_team)
        await self.session.commit()
        await self.session.refresh(instance=new_team)
        return new_team

    async def add_user_to_team(self, user: User, team_id: int) -> None:
        """
        Добавляет пользователя в команду

        Args:
            user - модель пользователя для добавления в команду
            team_id - ID целевой команды
        """
        user.team_id = team_id
        self.session.add(instance=user)
        await self.session.commit()
