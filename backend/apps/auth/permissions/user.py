from typing import List
from core.utils import PermissionDef

DEFINED_PERMISSIONS: List[PermissionDef] = [
    PermissionDef("user:create", "Allows creating new user items."),
    PermissionDef("user:list", "Allows list user items."),
    PermissionDef("user:read", "Allows viewing user items."),
    PermissionDef("user:update", "Allows updating existing user items."),
    PermissionDef("user:delete", "Allows deleting user items."),
]
