
from sqlalchemy import Column, DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, declared_attr
from sqlalchemy.sql import func



class TimestampMixin:
    @declared_attr
    def created_at(cls):
        return Column(DateTime, default=func.now(), nullable=False)

    @declared_attr
    def updated_at(cls):
        return Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)


class BaseModel(DeclarativeBase, TimestampMixin, AsyncAttrs):
    """
    Modelo base para todos os modelos de banco de dados.
    Inclui o mixin de timestamps e suporte a atributos assíncronos.
    """
    __abstract__ = True
