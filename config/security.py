from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import jwt
import bcrypt
import secrets

from config.settings import settings
from core.exceptions import UnauthorizedException


def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hash_bytes = bcrypt.hashpw(pwd_bytes, salt)
    return hash_bytes.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = plain_password.encode('utf-8')
    hash_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(pwd_bytes, hash_bytes)


# ==================== Funções de token JWT ====================

def create_access_token(data: Dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: Dict[str, Any]) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": int(expire.timestamp())})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise UnauthorizedException(detail="Could not validate credentials")


def is_jwt_token(token: str) -> bool:
    """
    Verifica se um token é um JWT válido.
    JWTs têm o formato: header.payload.signature (3 partes separadas por pontos)
    """
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return False
        # Tenta decodificar para verificar se é um JWT válido
        jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM], options={"verify_signature": False})
        return True
    except Exception:
        return False



# ==================== Funções de token opaco ====================

def generate_opaque_token() -> str:
    """
    Gera um token opaco aleatório e seguro.
    Tokens opacos são strings aleatórias que não contêm informação decodificável.
    """
    return secrets.token_urlsafe(32)  # 32 bytes = 256 bits de entropia


def get_opaque_token_expiry() -> datetime:
    """Retorna a data de expiração para um token de acesso opaco."""
    return datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)


def get_opaque_refresh_token_expiry() -> datetime:
    """Retorna a data de expiração para um token de refresh opaco."""
    return datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
