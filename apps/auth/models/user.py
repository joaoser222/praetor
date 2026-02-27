from sqlalchemy import Boolean, Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from core.base_model import BaseModel


class User(BaseModel):
    __tablename__ = "auth_users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String(100))
    
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    role_id = Column(Integer, ForeignKey("auth_roles.id"), nullable=True)

    role = relationship("Role", back_populates="users")
    user_permissions = relationship("UserPermission", back_populates="user")

    tokens = relationship("Token", back_populates="user")