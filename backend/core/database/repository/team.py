from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.core.database.models.teams import Team


class TeamRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_team_by_id(self, team_id: int) -> Team | None:
        stmt = (
            select(Team).where(Team.id == team_id).options(selectinload(Team.members))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
