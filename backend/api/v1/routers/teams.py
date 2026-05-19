from fastapi import APIRouter, HTTPException, status

from backend.api.dependencies.teams import TeamServiceDepends
from backend.core.schemas.team import TeamWithMembersRead
from backend.exceptions import TeamDoesNotExistsError


router = APIRouter(prefix="/teams", tags=["Команды"])


@router.get(
    "/{team_id}",
    response_model=TeamWithMembersRead,
    status_code=status.HTTP_200_OK,
    summary="Получить информацию о команде",
)
async def get_team(
    team_id: int,
    service: TeamServiceDepends,
):
    """
    Возвращает данные команды и список её участников.
    """
    try:
        team = await service.get_team(team_id=team_id)
        return team
    except TeamDoesNotExistsError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Команда не найдена",
        )
