from backend.api.dependencies.permissions import get_current_user
from backend.api.main import app
from backend.api.tests.test_tasks_api.get_user_override import override_get_regular_user
from backend.core.constants import TaskStatus


async def test_change_task_status(client, task_in_json):
    create_response = await client.post("/api/v1/tasks/", json=task_in_json)
    create_response_json = create_response.json()

    task_id = create_response_json.get("id")

    patch_data = {"status": TaskStatus.DONE}
    response = await client.patch(f"/api/v1/tasks/{task_id}/status/", json=patch_data)

    assert response.status_code == 200
    assert response.json().get("status") == TaskStatus.DONE


async def test_update_foreign_task_forbidden(client, task_in_json):
    create_response = await client.post("/api/v1/tasks/", json=task_in_json)
    task_id = create_response.json().get("id")

    old_dep = app.dependency_overrides.get(get_current_user)
    app.dependency_overrides[get_current_user] = override_get_regular_user

    patch_data = {"status": TaskStatus.DONE}
    response = await client.patch(f"/api/v1/tasks/{task_id}/status/", json=patch_data)

    if old_dep:
        app.dependency_overrides[get_current_user] = old_dep

    assert response.status_code == 403
    assert response.json()["detail"] == "Недостаточно прав для изменения статуса"


async def test_update_task_success(client, task_in_json):
    # Создаем исходную задачу
    create_response = await client.post("/api/v1/tasks/", json=task_in_json)
    task_id = create_response.json().get("id")

    # Отправляем данные для частичного обновления
    update_data = {"title": "Обновленный заголовок", "description": "Новые детали"}
    response = await client.patch(f"/api/v1/tasks/{task_id}/", json=update_data)

    data = response.json()

    assert response.status_code == 200
    assert data.get("title") == "Обновленный заголовок"
    assert data.get("description") == "Новые детали"
    # Убеждаемся, что остальные поля не затерлись
    assert data.get("status") == task_in_json["status"]


async def test_update_task_nonexistent_executor(client, task_in_json):
    create_response = await client.post("/api/v1/tasks/", json=task_in_json)
    task_id = create_response.json().get("id")

    # Пытаемся назначить пользователя, которого точно нет в БД
    update_data = {"executor_id": 999999}
    response = await client.patch(f"/api/v1/tasks/{task_id}/", json=update_data)

    assert response.status_code == 400
    # В exception_handlers.py UserDoesNotExistsError мапится на 400,
    # а в сервисе мы передаем этот текст
    assert "несуществующего исполнителя" in response.json()["detail"]
