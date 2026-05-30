from datetime import datetime, timezone

import pytest

from backend.core.constants import TaskStatus, RoleName
from backend.task.schemas import TaskCreate, TaskRead, CommentRead
from backend.user.schemas import UserDTO, RoleDTO


@pytest.fixture
def task_in():
    return TaskCreate(
        title="Тестовая задача",
        description="Описание тестовой задачи",
        status=TaskStatus.OPEN,
    )


@pytest.fixture
def mock_user_author():
    return UserDTO(
        id=1,
        email="author@test.com",
        hashed_password="hash",
        name="Author",
        role_id=3,
        role=RoleDTO(id=3, name=RoleName.USER),
        is_active=True,
    )


@pytest.fixture
def mock_user_stranger():
    return UserDTO(
        id=2,
        email="stranger@test.com",
        hashed_password="hash",
        name="Stranger",
        role_id=3,
        role=RoleDTO(id=3, name=RoleName.USER),
        is_active=True,
    )


@pytest.fixture
def sample_task():
    return TaskRead(
        id=1,
        title="Тест",
        description="Описание",
        status=TaskStatus.OPEN,
        author_id=1,  # ID совпадает с mock_user_author
        executor_id=None,
        created_at=datetime.now(timezone.utc),
    )


@pytest.fixture
def sample_comment():
    return CommentRead(
        id=1,
        task_id=1,
        author_id=1,
        text="Тестовый комментарий",
        created_at=datetime.now(timezone.utc),
    )
