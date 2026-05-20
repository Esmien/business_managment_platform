async def test_get_team_info_by_id_success(client, response_json):
    response = await client.get("/api/v1/teams/1")

    assert response.status_code == 200
    assert response_json == response.json()


async def test_get_team_info_by_id_not_exists(client):
    response = await client.get("/api/v1/teams/999")
    status = response.status_code

    assert status == 404


async def test_create_team_success(
    client,
    request_body_for_create_team,
    response_data_by_create_team,
    response_data_duplicate,
):
    request_duplicate = request_body_for_create_team.copy()
    request_duplicate["name"] = "Dummy name"

    response = await client.post("/api/v1/teams/", json=request_body_for_create_team)
    response_duplicate = await client.post("/api/v1/teams/", json=request_duplicate)

    response_json = response.json()
    response_duplicate_json = response_duplicate.json()

    for key, value in response_data_by_create_team.items():
        assert response_json.get(key) == value

    assert response.status_code == 201
    assert response_duplicate.status_code == 400
    assert response_duplicate_json == response_data_duplicate


async def test_create_team_duplicate_name(
    client, request_duplicate, response_data_duplicate
):
    response = await client.post("/api/v1/teams/", json=request_duplicate)

    response_json = response.json()

    assert response.status_code == 400
    assert response_json == response_data_duplicate
