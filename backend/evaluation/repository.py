from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.evaluation.models import Evaluation
from backend.evaluation.schemas import EvaluationRead, EvaluationCreateDTO


class EvaluationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add(self, evaluation: EvaluationCreateDTO) -> EvaluationRead:
        """
        Добавляет оценку к задаче

        Args:
            evaluation - модель оценки

        Returns:
            Оценка со всеми нужными полями
        """
        new_eval = Evaluation(**evaluation.model_dump(exclude_none=True))

        self.session.add(new_eval)
        await self.session.flush()
        await self.session.refresh(new_eval)

        return EvaluationRead.model_validate(obj=new_eval)

    async def get_by_task_id(self, task_id: int) -> EvaluationRead | None:
        """
        Ищет оценку по ID задачи

        Args:
            task_id - ID задачи, к которой ищется оценка

        Returns:
            Оценка или None, если оценка еще не стоит
        """
        stmt = select(Evaluation).where(Evaluation.task_id == task_id)
        result = await self.session.execute(stmt)
        eval_model = result.scalar_one_or_none()

        return EvaluationRead.model_validate(obj=eval_model) if eval_model else None
