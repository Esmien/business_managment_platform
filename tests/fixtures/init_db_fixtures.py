import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from backend.api.dependencies.uow import get_uow

from backend.api.dependencies.permissions import get_current_user
from backend.api.main import app
from backend.core.database.engine import Base
from backend.core.database.init_db import init_basic_data
from backend.core.uow import UnitOfWork
from backend.core.security import get_password_hash
from backend.team.models import Team
from backend.user.models import User


TEST_DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/test_business_db"

test_engine = create_async_engine(TEST_DB_URL, echo=False, poolclass=NullPool)
test_async_session_maker = async_sessionmaker(
    bind=test_engine, expire_on_commit=False, autoflush=False
)


async def override_get_session():
    async with test_async_session_maker() as session:
        yield session


async def override_get_current_user():
    async with test_async_session_maker() as session:
        stmt = select(User).where(User.email == "admin@admin.com")
        result = await session.execute(stmt)
        return result.scalar_one_or_none()


class TestUnitOfWork(UnitOfWork):
    def __init__(self):
        super().__init__()
        self.session_factory = test_async_session_maker


async def override_get_uow():
    return TestUnitOfWork()


app.dependency_overrides[get_uow] = override_get_uow
app.dependency_overrides[get_current_user] = override_get_current_user

TEAM_NAME = "Dummy name"
TEAM_CODE = "111111"

_PASSWORDS_CACHE: dict[str, str] = {}


async def _get_cached_password_hash(password: str) -> str:
    """Возвращает закешированный хеш или генерирует новый, если его еще нет"""
    if password not in _PASSWORDS_CACHE:
        _PASSWORDS_CACHE[password] = await get_password_hash(password)
    return _PASSWORDS_CACHE[password]


# Фикстура для структуры БД (выполняется 1 раз за сессию)
@pytest.fixture(scope="session", autouse=True)
async def prepare_schema():
    """Создает таблицы перед началом тестов и удаляет в конце"""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# 2. Фикстура для данных (выполняется перед каждым тестом)
@pytest.fixture(scope="function", autouse=True)
async def prepare_data():
    """Очищает таблицы и заливает базовые данные для каждого теста"""

    # 2.1 Жестко очищаем все таблицы
    async with test_engine.begin() as conn:
        # Собираем имена всех таблиц из метадаты
        table_names = ", ".join(Base.metadata.tables.keys())

        if table_names:
            # RESTART IDENTITY - сбрасывает счетчики (id=1)
            # CASCADE - игнорирует foreign keys и сносит связанные данные
            await conn.execute(
                text(f"TRUNCATE {table_names} RESTART IDENTITY CASCADE;")
            )

    # 2.2 Заливаем "чистые" дефолтные данные
    async with test_async_session_maker() as session:
        await init_basic_data(
            session=session, password_hasher=_get_cached_password_hash
        )
        team = Team(name=TEAM_NAME, invite_code=TEAM_CODE)
        session.add(team)
        await session.commit()
