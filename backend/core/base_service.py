from sqlalchemy.ext.asyncio import AsyncSession


class BaseService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def commit(self):
        """Confirma a transação atual."""
        await self.db.commit()

    async def rollback(self):
        """Desfaz a transação atual."""
        await self.db.rollback()

    async def refresh(self, instance: object):
        """Atualiza o estado da instância informada a partir do banco de dados."""
        await self.db.refresh(instance)
