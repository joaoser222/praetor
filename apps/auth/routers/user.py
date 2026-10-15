from typing import List
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from core.exceptions import NotFoundException
from .. import dependencies
from ..schemas import user as schemas
from ..repositories.user import UserRepository

router = APIRouter(
    prefix="/user",
    dependencies=[Depends(dependencies.get_current_active_superuser)]
)


@router.get("/", response_model=List[schemas.UserResponse])
async def get_all_users(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    """
    Recupera todos os usuários.

    Este endpoint é restrito a superusuários e suporta paginação.
    """
    repo = UserRepository(db)
    return await repo.get_multi(skip=skip, limit=limit)


@router.get("/{pk_type}", response_model=schemas.UserResponse)
async def get_user(id: int, db: AsyncSession = Depends(get_db)):
    """
    Obtém um usuário específico pelo seu ID.

    Este endpoint é restrito a superusuários.
    """
    repo = UserRepository(db)
    db_obj = await repo.get(pk=id)
    if not db_obj:
        raise NotFoundException(detail="User not found")
    return db_obj


@router.put("/{pk_type}", response_model=schemas.UserResponse)
async def update_user(id: int, user_in: schemas.UserUpdate, db: AsyncSession = Depends(get_db)):
    """
    Atualiza as informações de um usuário pelo seu ID.

    Este endpoint é restrito a superusuários.
    """
    repo = UserRepository(db)
    return await repo.update(pk=id, obj_in=user_in)


@router.delete("/{pk_type}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: int, db: AsyncSession = Depends(get_db)):
    """
    Remove um usuário pelo seu ID.

    Este endpoint é restrito a superusuários.
    """
    repo = UserRepository(db)
    await repo.delete(pk=id)
