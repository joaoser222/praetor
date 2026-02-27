from typing import List
from functools import wraps
from fastapi import Depends
from sqlalchemy.orm import selectinload
from apps.auth.dependencies import get_current_user
from apps.auth.models import User
from core.exceptions import ForbiddenException


def require_role(required_roles: List[str]):
    """
    Factory to create a dependency that checks if the current user
    has at least one of the required roles.
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
    Factory to create a dependency that checks if the current user
    has a specific permission through their roles.
    """
    async def permission_checker(current_user: User = Depends(get_current_user)) -> User:
        if current_user.is_superuser:
            return current_user

        user_permissions = set()
        
        # 1. Get permissions from the single role
        role = await current_user.awaitable_attrs.role
        if role:
            for role_perm in await role.awaitable_attrs.permissions:
                # Assuming role_perm is a RolePermission object, we need to access its permission
                perm = await role_perm.awaitable_attrs.permission
                user_permissions.add(perm.name)

        # 2. Get direct permissions allocated to the user
        for user_perm in await current_user.awaitable_attrs.user_permissions:
            perm = await user_perm.awaitable_attrs.permission
            user_permissions.add(perm.name)

        if required_permission not in user_permissions:
            raise ForbiddenException(detail=f"Action requires permission: '{required_permission}'")
        return current_user
    return permission_checker
