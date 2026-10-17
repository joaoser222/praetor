from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from core.dependencies import require_permission
from core.exceptions import NotFoundException
from ..schemas import user as schemas
from ..repositories.user import UserRepository

router = APIRouter(prefix="/user")


@router.get(
    "/",
    response_model=List[schemas.UserResponse],
    dependencies=[Depends(require_permission("user:list"))],
)
async def get_all_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """
    Recupera todos os usuários.

    Requer a permissão 'user:list' e suporta paginação.
    """
    repo = UserRepository(db)
    return await repo.get_multi(skip=skip, limit=limit)


@router.get(
    "/{user_id}",
    response_model=schemas.UserResponse,
    dependencies=[Depends(require_permission("user:read"))],
)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Obtém um usuário específico pelo seu ID. Requer 'user:read'."""
    repo = UserRepository(db)
    db_obj = await repo.get(user_id)
    if not db_obj:
        raise NotFoundException(detail="User not found")
    return db_obj


@router.put(
    "/{user_id}",
    response_model=schemas.UserResponse,
    dependencies=[Depends(require_permission("user:update"))],
)
async def update_user(user_id: int, user_in: schemas.UserUpdate, db: AsyncSession = Depends(get_db)):
    """Atualiza as informações de um usuário pelo seu ID. Requer 'user:update'."""
    repo = UserRepository(db)
    db_obj = await repo.update(pk=user_id, obj_in=user_in)
    if not db_obj:
        raise NotFoundException(detail="User not found")
    return db_obj


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("user:delete"))],
)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db)):
    """Remove um usuário pelo seu ID. Requer 'user:delete'."""
    repo = UserRepository(db)
    db_obj = await repo.get(user_id)
    if not db_obj:
        raise NotFoundException(detail="User not found")
    await repo.delete(pk=user_id)
