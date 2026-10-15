from typing import Optional
from datetime import datetime, timezone
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from core.base_repository import BaseRepository
from ..models.token import Token


class TokenRepository(BaseRepository[Token, dict, dict]):
    def __init__(self, db: AsyncSession):
        super().__init__(Token, db)

    async def get_by_token(self, token: str) -> Optional[Token]:
        """Obtém um token de refresh pelo seu valor."""
        query = select(self.model).where(
            and_(
                self.model.token == token,
                self.model.is_active == True
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_token(
        self,
        token: str,
        user_id: int,
        expires_at: datetime
    ) -> Token:
        """
        Cria um novo token de refresh.
        
        No modelo híbrido, apenas os tokens de refresh são armazenados no banco de dados.
        """
        db_token = Token(
            token=token,
            user_id=user_id,
            expires_at=expires_at,
            is_active=True
        )
        self.db.add(db_token)
        await self.db.commit()
        await self.db.refresh(db_token)
        return db_token

    async def revoke_token(self, token: str) -> bool:
        """Revoga um token de refresh (marca-o como inativo)."""
        db_token = await self.get_by_token(token)
        if db_token:
            db_token.is_active = False
            self.db.add(db_token)
            await self.db.commit()
            return True
        return False

    async def revoke_user_tokens(self, user_id: int) -> int:
        """Revoga todos os tokens de refresh de um usuário."""
        query = select(self.model).where(
            and_(
                self.model.user_id == user_id,
                self.model.is_active == True
            )
        )
        
        result = await self.db.execute(query)
        tokens = result.scalars().all()
        
        count = 0
        for token in tokens:
            token.is_active = False
            self.db.add(token)
            count += 1
        
        if count > 0:
            await self.db.commit()
        return count

    async def cleanup_expired_tokens(self) -> int:
        """Remove do banco de dados os tokens expirados."""
        now = datetime.now(timezone.utc)
        query = select(self.model).where(self.model.expires_at < now)
        result = await self.db.execute(query)
        expired_tokens = result.scalars().all()
        
        count = 0
        for token in expired_tokens:
            await self.db.delete(token)
            count += 1
        
        if count > 0:
            await self.db.commit()
        return count

    async def is_token_valid(self, token: str) -> bool:
        """Verifica se um token de refresh é válido (existe, está ativo e não expirou)."""
        db_token = await self.get_by_token(token)
        if not db_token:
            return False
        
        if not db_token.is_active:
            return False
        
        if db_token.expires_at < datetime.now(timezone.utc):
            return False
        
        return True
