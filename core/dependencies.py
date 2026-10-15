from typing import List
from functools import wraps
from fastapi import Depends
from sqlalchemy.orm import selectinload
from apps.auth.dependencies import get_current_user
from apps.auth.models import User
from core.exceptions import ForbiddenException


def require_role(required_roles: List[str]):
    """
    Fábrica para criar uma dependência que verifica se o usuário atual
    possui pelo menos um dos papéis exigidos.
    """
    async def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role_name = (await current_user.awaitable_attrs.role).name if await current_user.awaitable_attrs.role else None
        
        if not current_user.is_superuser:
            if not user_role_name or user_role_name not in required_roles:
                raise ForbiddenException(detail=f"Requires one of the following roles: {', '.join(required_roles)}")
        return current_user

    return role_checker


def require_permission(required_permission: str):
    """
    Fábrica para criar uma dependência que verifica se o usuário atual
    possui uma permissão específica por meio de seus papéis.
    """
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.is_superuser:
            return current_user

        user_permissions = set()
        
        # 1. Obtém as permissões do papel único
        role = await current_user.awaitable_attrs.role
        if role:
            for role_perm in await role.awaitable_attrs.permissions:
                # Assumindo que role_perm é um objeto RolePermission; precisamos acessar sua permission
                perm = await role_perm.awaitable_attrs.permission
                user_permissions.add(perm.name)

        # 2. Obtém as permissões atribuídas diretamente ao usuário
        for user_perm in await current_user.awaitable_attrs.user_permissions:
            perm = await user_perm.awaitable_attrs.permission
            user_permissions.add(perm.name)

        if required_permission not in user_permissions:
            raise ForbiddenException(detail=f"Action requires permission: '{required_permission}'")
        return current_user
    return permission_checker
