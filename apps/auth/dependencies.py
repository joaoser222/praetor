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
    FastAPI native security scheme extended to support HttpOnly cookies.
    This enables the 'Authorize' button in Swagger UI while maintaining
    the hybrid (Header + Cookie) authentication model.
    """
    async def __call__(self, request: Request) -> Optional[str]:
        # 1. Try to get token from standard Authorization header (FastAPI default)
        token: Optional[str] = await super().__call__(request)
        
        # 2. If not in header, try to get from cookie
        if not token:
            token = request.cookies.get("access_token")

        if not token:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return None

        return token


# Initialize the scheme pointing to the login endpoint
oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/api/auth/action/login")



async def get_token_payload(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    Decodes and validates the JWT token.
    """
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
    Get current user from database using the token payload.
    """
    user_id = payload.get("sub")
    if not user_id:
        raise UnauthorizedException(detail="Token missing user information")

    user_repo = UserRepository(db)
    user = await user_repo.get(int(user_id))
    
    if user is None or not user.status:
        raise UnauthorizedException(detail="User not found or inactive")
        
    return user


def get_current_active_superuser(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_superuser:
        raise ForbiddenException(detail="Superuser privileges required")
    return current_user