import pytest
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from backend.api.dependencies.uow import get_uow
from backend.core.constants import BusinessElementName, RoleName
from backend.core.database import load_all_models

from backend.api.dependencies.permissions import get_current_user
from backend.api.main import app
from backend.core.database.engine import Base
from backend.core.uow import UnitOfWork
from backend.rbac.models import AccessRule, BusinessElement
from backend.rbac.schemas import RBACPermissions
from backend.core.security import get_password_hash
from backend.team.models import Team
from backend.user.models import User, Role

load_all_models()


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


class InitDatabase:
    PASSWORDS_CACHE = {}

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create(self, model, **kwargs):
        """Удобный хелпер: ищет запись, если нет - создает"""
        stmt = select(model).filter_by(**kwargs)
        result = await self.session.execute(stmt)
        instance = result.scalar_one_or_none()

        if not instance:
            instance = model(**kwargs)
            self.session.add(instance)
            await self.session.flush()
            await self.session.refresh(instance)
        return instance

    async def _create_access_rule_if_not_exists(
        self, role_id: int, element_id: int, permissions: RBACPermissions
    ):
        query = select(AccessRule).where(
            AccessRule.role_id == role_id,
            AccessRule.business_element_id == element_id,
        )
        result = await self.session.execute(query)
        rule = result.scalar_one_or_none()

        if rule is None:
            rule = AccessRule(
                role_id=role_id,
                business_element_id=element_id,
                **permissions.model_dump(exclude_none=True),
            )
            self.session.add(rule)

    async def get_cached_password_hash(self, password: str) -> str:
        """Возвращает закешированный хеш или генерирует новый, если его еще нет"""
        if password not in self.PASSWORDS_CACHE:
            self.PASSWORDS_CACHE[password] = await get_password_hash(password)
        return self.PASSWORDS_CACHE[password]

    async def run(self):
        admin_role = await self.get_or_create(Role, name=RoleName.ADMIN)
        manager_role = await self.get_or_create(Role, name=RoleName.MANAGER)
        user_role = await self.get_or_create(Role, name=RoleName.USER)

        roles_map = {"admin": admin_role, "manager": manager_role, "user": user_role}

        for role in roles_map:
            email = f"{role}@{role}.com"
            query = select(User).filter_by(email=email)
            result = await self.session.execute(query)
            existing_user = result.scalar_one_or_none()

            if not existing_user:
                new_user = User(
                    email=email,
                    hashed_password=await self.get_cached_password_hash(role),
                    role_id=roles_map[role].id,
                    name=role.title(),
                )
                self.session.add(new_user)
                await self.session.flush()
                await self.session.refresh(new_user)

        inactive_user = User(
            email="inactive_user@user.com",
            hashed_password=await self.get_cached_password_hash("user"),
            role_id=roles_map["user"].id,
            name="Inactive user",
            is_active=False,
        )
        self.session.add(inactive_user)
        await self.session.flush()
        await self.session.refresh(inactive_user)

        permissions_map = {
            "admin": RBACPermissions(
                read_all_permission=True,
                update_all_permission=True,
                delete_all_permission=True,
                create_permission=True,
                read_permission=True,
                update_permission=True,
                delete_permission=True,
            ),
            "manager": RBACPermissions(
                read_all_permission=True,
                create_permission=True,
                read_permission=True,
                update_permission=True,
            ),
            "user": RBACPermissions(read_permission=True),
        }

        # Создаем бизнес-элементы для проверки RBAC
        teams_element = await self.get_or_create(
            BusinessElement, name=BusinessElementName.TEAMS
        )

        for key, value in roles_map.items():
            await self._create_access_rule_if_not_exists(
                role_id=value.id,
                element_id=teams_element.id,
                permissions=permissions_map[key],
            )

        await self.session.commit()


# 1. Фикстура для структуры БД (выполняется 1 раз за сессию)
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
        init_db = InitDatabase(session=session)
        await init_db.run()
        team = Team(name=TEAM_NAME, invite_code=TEAM_CODE)
        session.add(team)
        await session.commit()
