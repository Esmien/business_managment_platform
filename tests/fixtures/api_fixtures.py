import pytest
from httpx import AsyncClient, ASGITransport
from backend.api.main import app
# ----------------- Фикстуры с данными -----------------


@pytest.fixture
async def client():

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
        await ac.aclose()


@pytest.fixture
def response_json():
    return {
        "name": "Dummy name",
        "description": None,
        "id": 1,
        "invite_code": "111111",
        "members": [],
    }


@pytest.fixture
def request_body_for_create_team():
    return {"name": "New Team"}


@pytest.fixture
def response_data_by_create_team():
    return {"name": "New Team", "description": None, "id": 2}


@pytest.fixture
def request_duplicate():
    return {"name": "Dummy name"}


@pytest.fixture
def response_data_duplicate():
    return {"detail": "Команда с таким названием уже существует"}
