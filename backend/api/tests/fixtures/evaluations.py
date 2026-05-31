import pytest


@pytest.fixture
def evaluation_data():
    return {"value": 5, "comment": "Отличная работа, все в срок!"}


@pytest.fixture
async def closed_task_id(client, closed_task_json) -> int:
    """Создает завершенную задачу через API и возвращает её ID"""
    response = await client.post("/api/v1/tasks/", json=closed_task_json)
    assert response.status_code == 201, "Не удалось создать closed_task для теста"
    return response.json()["id"]


@pytest.fixture
async def open_task_id(client, open_task_json) -> int:
    """Создает открытую задачу через API и возвращает её ID"""
    response = await client.post("/api/v1/tasks/", json=open_task_json)
    assert response.status_code == 201, "Не удалось создать open_task для теста"
    return response.json()["id"]
