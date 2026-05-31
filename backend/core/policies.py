from backend.core.constants import RoleName, BusinessElementName, AccessLevel
from backend.rbac.schemas import AccessRules

# Структура: { Роль: { Бизнес-сущность: { действие: уровень_доступа } } }
DEFAULT_POLICIES = {
    RoleName.ADMIN: {
        BusinessElementName.TASKS: AccessRules(
            create=AccessLevel.ALL,
            read=AccessLevel.ALL,
            update=AccessLevel.ALL,
            delete=AccessLevel.ALL,
            change_status=AccessLevel.ALL,
        ).model_dump(exclude_none=True),
        BusinessElementName.COMMENTS: AccessRules(
            create=AccessLevel.ALL,
            read=AccessLevel.ALL,
            update=AccessLevel.ALL,
            delete=AccessLevel.ALL,
        ).model_dump(exclude_none=True),
        BusinessElementName.TEAMS: AccessRules(
            create=AccessLevel.ALL,
            read=AccessLevel.ALL,
            update=AccessLevel.ALL,
            delete=AccessLevel.ALL,
        ).model_dump(exclude_none=True),
        BusinessElementName.USERS: AccessRules(
            create=AccessLevel.ALL,
            read=AccessLevel.ALL,
            update=AccessLevel.ALL,
            delete=AccessLevel.ALL,
        ).model_dump(exclude_none=True),
    },
    RoleName.MANAGER: {
        BusinessElementName.TASKS: AccessRules(
            create=AccessLevel.ALL,
            read=AccessLevel.ALL,
            update=AccessLevel.ALL,
            delete=AccessLevel.ALL,
            change_status=AccessLevel.ALL,
        ).model_dump(exclude_none=True),
        BusinessElementName.COMMENTS: AccessRules(
            create=AccessLevel.ALL,
            read=AccessLevel.ALL,
            update=AccessLevel.ALL,
            delete=AccessLevel.ALL,
        ).model_dump(exclude_none=True),
        BusinessElementName.TEAMS: AccessRules(
            create=AccessLevel.ALL,
            read=AccessLevel.ALL,
            update=AccessLevel.ALL,
            delete=AccessLevel.ALL,
        ).model_dump(exclude_none=True),
        BusinessElementName.USERS: AccessRules(read=AccessLevel.ALL).model_dump(
            exclude_none=True
        ),
    },
    RoleName.USER: {
        # Вот тут вся магия ABAC: доступ только причастным (participant/author)
        BusinessElementName.TASKS: AccessRules(
            create=AccessLevel.ALL,
            read=AccessLevel.PARTICIPANT,
            update=AccessLevel.AUTHOR,
            delete=AccessLevel.AUTHOR,
            change_status=AccessLevel.PARTICIPANT,
        ).model_dump(exclude_none=True),
        BusinessElementName.COMMENTS: AccessRules(
            create=AccessLevel.PARTICIPANT,
            read=AccessLevel.PARTICIPANT,
            update=AccessLevel.AUTHOR,
            delete=AccessLevel.AUTHOR,
        ).model_dump(exclude_none=True),
        BusinessElementName.TEAMS: AccessRules(read=AccessLevel.PARTICIPANT).model_dump(
            exclude_none=True
        ),
        BusinessElementName.USERS: AccessRules(read=AccessLevel.ALL).model_dump(
            exclude_none=True
        ),
    },
}
