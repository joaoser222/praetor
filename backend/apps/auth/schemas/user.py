from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

# Propriedades compartilhadas
class UserBase(BaseModel):
    email: str
    username: str
    full_name: Optional[str] = None
    is_active: bool = True
    is_superuser: bool = False

# Propriedades recebidas via API na criação
class UserCreate(BaseModel):
    email: str
    username: str
    password: str
    full_name: Optional[str] = None
    is_superuser: bool = False

# Propriedades recebidas via API na atualização
class UserUpdate(BaseModel):
    email: Optional[str] = None
    username: Optional[str] = None
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: Optional[str] = Field(
        default=None,
        description=(
            "Refresh token opcional. Quando ausente, o token é lido do cookie "
            "HttpOnly 'refresh_token' (fluxo cookie-first do SPA)."
        ),
    )

# Propriedades retornadas ao cliente
class UserResponse(UserBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

# Propriedades do token
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    auth_type: str = Field(
        default="hybrid",
        description="Authentication type: always 'hybrid' (JWT access + Opaque refresh)"
    )
