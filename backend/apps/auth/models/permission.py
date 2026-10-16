from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from core.base_model import BaseModel

class Permission(BaseModel):
    __tablename__ = "auth_permissions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String(255))
    roles = relationship("RolePermission", back_populates="permission")