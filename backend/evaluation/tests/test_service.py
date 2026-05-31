import pytest
from unittest.mock import MagicMock

from backend.core.constants import TaskStatus
from backend.evaluation.schemas import EvaluationCreate, EvaluationCreateDTO
from backend.exceptions import AccessDeniedError, TaskDoesNotCompletedError


async def test_evaluate_task_access_denied(eval_service, test_user):
    # Принудительно забираем права для этого теста
    eval_service.rbac.check_permission.return_value = False

    evaluation_in = EvaluationCreate(value=5, comment="Test")

    with pytest.raises(AccessDeniedError, match="Недостаточно прав"):
        await eval_service.evaluate_task(
            task_id=1, evaluation_in=evaluation_in, user=test_user
        )


async def test_evaluate_task_not_completed(eval_service, mock_uow, test_user):
    mock_task = MagicMock()
    mock_task.status = TaskStatus.OPEN
    mock_uow.tasks.get_task_by_id.return_value = mock_task

    evaluation_in = EvaluationCreate(value=5)

    with pytest.raises(TaskDoesNotCompletedError, match="Задача еще не выполнена"):
        await eval_service.evaluate_task(
            task_id=1, evaluation_in=evaluation_in, user=test_user
        )


async def test_evaluate_task_success(eval_service, mock_uow, test_user):
    mock_task = MagicMock()
    mock_task.status = TaskStatus.DONE
    mock_uow.tasks.get_task_by_id.return_value = mock_task
    mock_uow.evaluations.get_by_task_id.return_value = None

    mock_uow.evaluations.add.return_value = "saved_evaluation_mock"

    evaluation_in = EvaluationCreate(value=5, comment="Good")

    result = await eval_service.evaluate_task(
        task_id=1, evaluation_in=evaluation_in, user=test_user
    )

    mock_uow.commit.assert_awaited_once()
    assert result == "saved_evaluation_mock"

    # Проверяем, что в репозиторий улетела правильная DTO
    called_args = mock_uow.evaluations.add.call_args[0][0]
    assert isinstance(called_args, EvaluationCreateDTO)
    assert called_args.value == 5
