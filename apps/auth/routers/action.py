from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from config.database import get_db
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
    """Registra um novo usuário."""
    # O registro público nunca concede privilégios de superusuário.
    user_in = user_in.model_copy(update={"is_superuser": False})
    user_service = UserService(db)
    return await user_service.create_user(user_in)

@router.post("/login", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Autentica o usuário e retorna os tokens usando o modelo híbrido.
    Suportar OAuth2PasswordRequestForm permite usar o recurso 'Authorize' do Swagger UI.
    """
    user_service = UserService(db)
    # OAuth2PasswordRequestForm usa o campo 'username', que mapeamos para 'email'
    return await user_service.authenticate_user(
        form_data.username, 
        form_data.password
    )


@router.post("/refresh", response_model=schemas.Token)
async def refresh_access_token(
    refresh_data: schemas.RefreshTokenRequest, db: AsyncSession = Depends(get_db)
):
    """
    Renova o token de acesso usando um token de refresh.
    
    Este endpoint:
    1. Valida o token de refresh opaco armazenado no banco de dados
    2. Gera um novo token de acesso JWT
    3. Gera um novo token de refresh (rotação de token por segurança)
    4. Revoga o token de refresh antigo
    
    Isso permite:
    - Revogar sessões de usuários invalidando tokens de refresh no banco de dados
    - Manter a performance do JWT (sem consulta ao banco para tokens de acesso)
    - Ter controle refinado sobre as sessões ativas
    """
    user_service = UserService(db)
    return await user_service.refresh_access_token(refresh_data.refresh_token)

@router.post("/logout")
async def logout(
    refresh_data: schemas.RefreshTokenRequest, db: AsyncSession = Depends(get_db)
):
    """
    Faz logout do usuário revogando o token de refresh.
    
    Isso invalida o token de refresh, impedindo que ele seja usado
    para gerar novos tokens de acesso. O token de acesso atual (JWT)
    continuará válido até expirar (curta duração, tipicamente 30 minutos).
    
    Para revogar todas as sessões, use o endpoint /logout/all.
    """
    user_service = UserService(db)
    return await user_service.logout(refresh_data.refresh_token)

@router.post("/logout/all")
async def logout_all_sessions(
    current_user: schemas.UserResponse = Depends(dependencies.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Faz logout do usuário de todas as sessões revogando todos os tokens de refresh.
    
    Isso é útil por motivos de segurança:
    - Troca de senha
    - Detecção de atividade suspeita
    - Pedido do usuário para sair de todos os dispositivos
    
    Observação: o token de acesso atual (JWT) continuará válido até expirar.
    """
    user_service = UserService(db)
    return await user_service.logout_all_sessions(current_user.id)


@router.get("/profile", response_model=schemas.UserResponse)
async def read_users_me(current_user: schemas.UserResponse = Depends(dependencies.get_current_user)):
    """Obtém o usuário logado atualmente."""
    return current_user
