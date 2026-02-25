from typing import List
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
from core.exceptions import NotFoundException
from .. import dependencies
from ..schemas import user as schemas
from ..services.user import UserService

router = APIRouter(prefix="/action")

@router.post(
    "/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED 
)
async def register_user(
    user_in: schemas.UserCreate, db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    user_service = UserService(db)
    return await user_service.create_user(user_in)

@router.post("/login", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate user and return tokens using the hybrid model.
    Supporting OAuth2PasswordRequestForm allows using Swagger UI's 'Authorize' feature.
    """
    user_service = UserService(db)
    # OAuth2PasswordRequestForm uses 'username' field, which we map to 'email'
    return await user_service.authenticate_user(
        form_data.username, 
        form_data.password
    )


@router.post("/refresh", response_model=schemas.Token)
async def refresh_access_token(
    refresh_data: schemas.RefreshTokenRequest, db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using a refresh token.
    
    This endpoint:
    1. Validates the opaque refresh token stored in the database
    2. Generates a new JWT access token
    3. Generates a new refresh token (token rotation for security)
    4. Revokes the old refresh token
    
    This allows you to:
    - Revoke user sessions by invalidating refresh tokens in the database
    - Maintain JWT performance (no DB lookup for access tokens)
    - Have fine-grained control over active sessions
    """
    user_service = UserService(db)
    return await user_service.refresh_access_token(refresh_data.refresh_token)

@router.post("/logout")
async def logout(
    refresh_data: schemas.RefreshTokenRequest, db: AsyncSession = Depends(get_db)
):
    """
    Logout user by revoking the refresh token.
    
    This invalidates the refresh token, preventing it from being used
    to generate new access tokens. The current access token (JWT) will
    remain valid until it expires (short-lived, typically 30 minutes).
    
    To revoke all sessions, use /logout/all endpoint.
    """
    user_service = UserService(db)
    return await user_service.logout(refresh_data.refresh_token)

@router.post("/logout/all")
async def logout_all_sessions(
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Logout user from all sessions by revoking all refresh tokens.
    
    This is useful for security purposes:
    - Password change
    - Suspicious activity detected
    - User request to logout from all devices
    
    Note: Current access token (JWT) will remain valid until expiration.
    """
    user_service = UserService(db)
    return await user_service.logout_all_sessions(current_user.id)


@router.get("/profile", response_model=schemas.UserResponse)
async def read_users_me(current_user: schemas.UserResponse = Depends(dependencies.get_current_user)):
    """Get current logged-in user."""
    return current_user