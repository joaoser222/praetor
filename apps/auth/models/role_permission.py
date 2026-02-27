from sqlalchemy import Column, Integer, String,ForeignKey
from sqlalchemy.orm import relationship
from core.base_model import BaseModel

class RolePermission(BaseModel):
    __tablename__ = "auth_role_permissions"
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("auth_roles.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("auth_permissions.id"), nullable=False)
    role = relationship("Role", back_populates="permissions")
    permission = relationship("Permission", back_populates="roles")
