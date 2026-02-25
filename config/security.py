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


# ==================== JWT Token Functions ====================

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
    Check if a token is a valid JWT.
    JWTs have the format: header.payload.signature (3 parts separated by dots)
    """
    try:
        parts = token.split('.')
        if len(parts) != 3:
            return False
        # Try to decode to verify if it's a valid JWT
        jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM], options={"verify_signature": False})
        return True
    except Exception:
        return False



# ==================== Opaque Token Functions ====================

def generate_opaque_token() -> str:
    """
    Generate a random and secure opaque token.
    Opaque tokens are random strings that don't contain decodable information.
    """
    return secrets.token_urlsafe(32)  # 32 bytes = 256 bits of entropy


def get_opaque_token_expiry() -> datetime:
    """Return the expiration date for an opaque access token."""
    return datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)


def get_opaque_refresh_token_expiry() -> datetime:
    """Return the expiration date for an opaque refresh token."""
    return datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)