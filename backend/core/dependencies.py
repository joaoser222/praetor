from typing import Any, List
from fastapi import Depends

from core.exceptions import ForbiddenException


def _get_current_user_dependency():
    """
    Resolve a dependência do usuário atual de forma preguiçosa.

    O núcleo (core) não deve depender de um app específico no momento do import.
    A importação só acontece quando a dependência é montada por um router.

    Returns:
        A função de dependência que retorna o usuário autenticado.
    """
    from apps.auth.dependencies import get_current_user

    return get_current_user


def require_role(required_roles: List[str]):
    """
    Fábrica para criar uma dependência que verifica se o usuário atual
    possui pelo menos um dos papéis exigidos.
    """

    async def role_checker(current_user: Any = Depends(_get_current_user_dependency())):
        role = await current_user.awaitable_attrs.role
        user_role_name = role.name if role else None

        if not current_user.is_superuser:
            if not user_role_name or user_role_name not in required_roles:
                raise ForbiddenException(
                    detail=f"Requires one of the following roles: {', '.join(required_roles)}"
                )
        return current_user

    return role_checker


def require_permission(required_permission: str):
    """
    Fábrica para criar uma dependência que verifica se o usuário atual
    possui uma permissão específica por meio de seus papéis.
    """

    async def permission_checker(current_user: Any = Depends(_get_current_user_dependency())):
        if current_user.is_superuser:
            return current_user

        user_permissions = set()

        # 1. Obtém as permissões do papel único
        role = await current_user.awaitable_attrs.role
        if role:
            for role_perm in await role.awaitable_attrs.permissions:
                perm = await role_perm.awaitable_attrs.permission
                user_permissions.add(perm.name)

        # 2. Obtém as permissões atribuídas diretamente ao usuário
        for user_perm in await current_user.awaitable_attrs.user_permissions:
            perm = await user_perm.awaitable_attrs.permission
            user_permissions.add(perm.name)

        if required_permission not in user_permissions:
            raise ForbiddenException(
                detail=f"Action requires permission: '{required_permission}'"
            )
        return current_user

    return permission_checker
