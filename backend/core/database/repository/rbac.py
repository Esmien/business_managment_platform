from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.database.models.rbac import AccessRule, BusinessElement


class RbacRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_access_rule(
        self, role_id: int, element_name: str
    ) -> AccessRule | None:
        """
        Возвращает правило доступа для указанной роли на указанный ресурс.

        Args:
            role_id - ID роли
            element_name - название ресурса

        Returns:
            AccessRule если правило найдено, иначе None
        """
        stmt = (
            select(AccessRule)
            .join(BusinessElement)
            .where(
                AccessRule.role_id == role_id,
                BusinessElement.name == element_name,
            )
        )

        result = await self.session.execute(statement=stmt)

        return result.scalar_one_or_none()
