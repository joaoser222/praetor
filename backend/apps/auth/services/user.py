from sqlalchemy.ext.asyncio import AsyncSession

from config.security import (
    create_access_token,
    get_password_hash,
    verify_password,
    generate_opaque_token,
    get_opaque_refresh_token_expiry,
)
from config.time import utc_now
from core.base_service import BaseService
from core.exceptions import UnauthorizedException, ValidationException
from ..models import User
from ..repositories.user import UserRepository
from ..repositories.token import TokenRepository
from ..schemas.user import UserCreate

class UserService(BaseService):
    def __init__(self, db: AsyncSession):
        super().__init__(db)
        self.repo = UserRepository(db)
        self.token_repo = TokenRepository(db)

    async def create_user(self, user_in: UserCreate) -> User:
        """Cria um novo usuário."""
        if await self.repo.get_by_email(user_in.email):
            raise ValidationException(detail="Email already registered")
        if await self.repo.get_by_username(user_in.username):
            raise ValidationException(detail="Username already taken")
            
        hashed_password = get_password_hash(user_in.password)
        user_data = user_in.model_dump(exclude={"password"})
        user_data["hashed_password"] = hashed_password
        
        # Cria manualmente a instância do modelo para usar hashed_password
        db_user = User(**user_data)
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        return db_user

    async def authenticate_user(self, email: str, password: str) -> dict:
        """
        Autentica um usuário e retorna os tokens usando o modelo híbrido.
        
        Modelo Híbrido:
        - Access Token: JWT (stateless, performático, sem consulta ao banco)
        - Refresh Token: Opaco no banco (pode ser revogado facilmente)
        
        Isso combina o melhor dos dois mundos:
        - Performance: tokens de acesso JWT não exigem consultas ao banco
        - Segurança: tokens de refresh podem ser revogados ao serem removidos do banco
        
        Args:
            email: E-mail do usuário
            password: Senha do usuário
        
        Returns:
            dict com access_token (JWT), refresh_token (opaco), token_type e auth_type
        """
        user = await self.repo.get_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise UnauthorizedException(detail="Incorrect email or password")
        if not user.is_active:
            raise UnauthorizedException(detail="Inactive user")

        # Gera o token de acesso JWT (stateless, performático)
        token_data = {"sub": str(user.id)}
        access_token = create_access_token(data=token_data)
        
        # Gera o token de refresh (armazenado no banco, pode ser revogado)
        refresh_token_value = generate_opaque_token()
        await self.token_repo.create_token(
            token=refresh_token_value,
            user_id=user.id,
            expires_at=get_opaque_refresh_token_expiry()
        )
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token_value,
            "token_type": "bearer",
            "auth_type": "hybrid"
        }

    async def refresh_access_token(self, refresh_token: str) -> dict:
        """
        Renova um token de acesso usando um token de refresh.
        
        Este método valida o token de refresh opaco armazenado no banco de dados
        e gera um novo token de acesso JWT.
        
        Args:
            refresh_token: O token de refresh opaco
        
        Returns:
            dict com o novo access_token, refresh_token, token_type e auth_type
        
        Raises:
            UnauthorizedException: Se o token de refresh for inválido, expirado ou revogado
        """
        # Valida o token de refresh no banco de dados
        token_repo = TokenRepository(self.db)
        db_token = await token_repo.get_by_token(refresh_token)
        
        if not db_token:
            raise UnauthorizedException(detail="Refresh token not found")
        
        if not db_token.is_active:
            raise UnauthorizedException(detail="Refresh token has been revoked")
        
        # Verifica a expiração
        if db_token.expires_at < utc_now():
            raise UnauthorizedException(detail="Refresh token has expired")
        
        # Obtém o usuário
        user = await self.repo.get(db_token.user_id)
        if not user or not user.is_active:
            raise UnauthorizedException(detail="User not found or inactive")
        
        # Revoga o token de refresh antigo (rotação de token por segurança)
        await token_repo.revoke_token(refresh_token)
        
        # Gera um novo token de acesso JWT
        token_data = {"sub": str(user.id)}
        new_access_token = create_access_token(data=token_data)
        
        # Gera um novo token de refresh
        new_refresh_token_value = generate_opaque_token()
        await token_repo.create_token(
            token=new_refresh_token_value,
            user_id=user.id,
            expires_at=get_opaque_refresh_token_expiry()
        )
        
        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token_value,
            "token_type": "bearer",
            "auth_type": "hybrid"
        }

    async def logout(self, refresh_token: str) -> dict:
        """
        Faz logout do usuário revogando o token de refresh.
        
        Isso invalida o token de refresh, impedindo que ele seja usado
        para gerar novos tokens de acesso. O token de acesso atual continuará
        válido até expirar (JWT de curta duração).
        
        Args:
            refresh_token: O token de refresh a ser revogado
        
        Returns:
            dict com mensagem de sucesso
        
        Raises:
            UnauthorizedException: Se o token de refresh for inválido
        """
        token_repo = TokenRepository(self.db)
        revoked = await token_repo.revoke_token(refresh_token)
        
        if not revoked:
            raise UnauthorizedException(detail="Invalid refresh token")
        
        return {"message": "Successfully logged out"}

    async def logout_all_sessions(self, user_id: int) -> dict:
        """
        Faz logout do usuário de todas as sessões revogando todos os tokens de refresh.
        
        Isso é útil por motivos de segurança (por exemplo, troca de senha,
        atividade suspeita ou ação de administrador).
        
        Args:
            user_id: O ID do usuário para revogar todos os tokens
        
        Returns:
            dict com a contagem de tokens revogados
        """
        token_repo = TokenRepository(self.db)
        count = await token_repo.revoke_user_tokens(user_id=user_id)
        
        return {
            "message": f"Successfully logged out from {count} session(s)",
            "revoked_sessions": count
        }
