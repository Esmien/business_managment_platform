from loguru import logger

from backend.rbac.repository import RbacRepository


class RbacService:
    def __init__(self, repo: RbacRepository):
        self.repo = repo

    async def check_permission(
        self, role_id: int, element_name: str, permission: str
    ) -> bool:
        """
        Проверяет права доступа к ресурсу для роли

        Args:
            role_id - проверяемая роль
            element_name - ресурс, к которому проверяется доступ
            permission - правило доступа к ресурсу

        Returns:
            True - если доступ разрешен, иначе False
        """
        rule = await self.repo.get_access_rule(role_id, element_name)

        if not rule:
            return False

        # Если передано несуществующее правило
        if not hasattr(rule, permission):
            logger.warning(f"Неизвестный permission: {permission}")
            return False

        return getattr(rule, permission, False)
