async def test_create_task_success(client, task_in_json):
    response = await client.post("/api/v1/tasks/", json=task_in_json)

    data = response.json()

    assert response.status_code == 201
    assert data.get("title") == task_in_json["title"]
    assert "id" in data
    assert data.get("author_id") == 1