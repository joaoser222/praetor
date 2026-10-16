from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Dict, Any
from config.database import get_db
from config.security import decode_token, is_jwt_token
from core.exceptions import UnauthorizedException, ForbiddenException
from .models import User
from .repositories.user import UserRepository


class OAuth2PasswordBearerWithCookie(OAuth2PasswordBearer):
    """
    Esquema de segurança nativo do FastAPI estendido para suportar cookies HttpOnly.
    Isso habilita o botão 'Authorize' do Swagger UI, mantendo o modelo híbrido
    de autenticação (Header + Cookie).
    """
    async def __call__(self, request: Request) -> Optional[str]:
        # 1. Tenta obter o token do header Authorization padrão (padrão do FastAPI).
        #    O esquema é criado com auto_error=False, então a ausência de header
        #    devolve None em vez de lançar 401 — permitindo o fallback abaixo.
        token: Optional[str] = await super().__call__(request)

        # 2. Se não estiver no header, tenta obter do cookie HttpOnly.
        if not token:
            token = request.cookies.get("access_token")

        # A validação (e o 401 quando não há token) fica a cargo de `get_token_payload`.
        return token


# Inicializa o esquema apontando para o endpoint de login.
# auto_error=False é essencial: sem ele o OAuth2PasswordBearer lançaria 401
# ANTES de chegarmos ao fallback de cookie (que nunca seria alcançado).
oauth2_scheme = OAuth2PasswordBearerWithCookie(
    tokenUrl="/api/auth/action/login", auto_error=False
)


async def get_token_payload(token: Optional[str] = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Decodifica e valida o token JWT (vindo do header Authorization ou do cookie HttpOnly).
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not is_jwt_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format",
        )
    
    try:
        payload = decode_token(token)
        if "sub" not in payload:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        return payload
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired or invalid",
        )


async def get_current_user(
    payload: Dict[str, Any] = Depends(get_token_payload),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Obtém o usuário atual a partir do banco de dados usando o payload do token.
    """
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException(detail="Token missing user information")

    user_repo = UserRepository(db)
    user = await user_repo.get(int(user_id))
    
    if user is None or not user.is_active:
        raise UnauthorizedException(detail="User not found or inactive")
        
    return user


def get_current_active_superuser(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superuser:
        raise ForbiddenException(detail="Superuser privileges required")
    return current_user
