from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from core.base_model import BaseModel

class UserPermission(BaseModel):
    __tablename__ = "auth_user_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("auth_users.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("auth_permissions.id"), nullable=False)
    
    user = relationship("User", back_populates="user_permissions")
    permission = relationship("Permission")
