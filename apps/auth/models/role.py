from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from core.base_model import BaseModel

class Role(BaseModel):
    __tablename__ = "auth_roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(255))

    permissions = relationship(
        "RolePermission", back_populates="role", cascade="all, delete-orphan"
    )
    users = relationship("User", back_populates="role")
    

