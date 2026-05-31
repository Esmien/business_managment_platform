import pytest
from backend.evaluation.schemas import EvaluationCreateDTO


@pytest.mark.asyncio
async def test_repository_add_and_get(eval_repo, test_task_db, test_user_db):
    dto_in = EvaluationCreateDTO(
        value=4,
        comment="Test repo",
        task_id=test_task_db.id,
        evaluator_id=test_user_db.id,
    )

    saved_eval = await eval_repo.add(dto_in)

    assert saved_eval.id is not None
    assert saved_eval.value == 4
    assert saved_eval.comment == "Test repo"

    fetched_eval = await eval_repo.get_by_task_id(test_task_db.id)

    assert fetched_eval is not None
    assert fetched_eval.id == saved_eval.id
    assert fetched_eval.task_id == test_task_db.id
