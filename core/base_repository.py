from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from core.base_model import BaseModel as _BaseModel

ModelType = TypeVar("ModelType", bound=_BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType], db: AsyncSession):
        self.model = model
        self.db = db

    async def get(self, pk: Any) -> Optional[ModelType]:
        """Obtém um único registro pela chave primária."""
        result = await self.db.get(self.model, pk)
        return result

    async def get_multi(self, *, skip: int = 0, limit: int = 100) -> List[ModelType]:
        """Obtém múltiplos registros com paginação."""
        query = select(self.model).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create(self, *, obj_in: CreateSchemaType) -> ModelType:
        """Cria um novo registro."""
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(self, *, pk: Any, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        """Atualiza um registro existente."""
        db_obj = await self.get(pk)
        if not db_obj:
            return None
        
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
            
        self.db.add(db_obj)
        await self.db.commit()
        await self.db.refresh(db_obj)
        return db_obj

    async def delete(self, *, pk: Any) -> Optional[ModelType]:
        """Remove um registro."""
        db_obj = await self.get(pk)
        if db_obj:
            await self.db.delete(db_obj)
            await self.db.commit()
        return db_obj

    async def get_by_field(self, field: str, value: Any) -> Optional[ModelType]:
        """Obtém um único registro por um campo específico."""
        query = select(self.model).where(getattr(self.model, field) == value)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
