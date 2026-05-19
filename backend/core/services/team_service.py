from backend.core.database.repository.team import TeamRepository
from backend.exceptions import TeamDoesNotExistsError


class TeamService:
    def __init__(self, repo: TeamRepository):
        self.repo = repo

    async def get_team(self, team_id: int):
        team = await self.repo.get_team_by_id(team_id)

        if team is None:
            raise TeamDoesNotExistsError

        return team
