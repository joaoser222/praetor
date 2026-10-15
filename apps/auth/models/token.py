from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from core.base_model import BaseModel


class Token(BaseModel):
    """
    Modelo para armazenar tokens de refresh no banco de dados.

    No modelo híbrido, apenas os tokens de refresh são armazenados no banco de dados.
    Os tokens de acesso são JWT (stateless) e não precisam ser armazenados.
    """
    __tablename__ = "auth_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(255), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("auth_users.id"), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

    # Relacionamento com o usuário
    user = relationship("User", back_populates="tokens")
