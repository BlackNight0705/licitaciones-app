from email.policy import default

from sqlalchemy import Boolean, Column, Integer, String
from backend.app.core.database import Base
from .auditMixin import AuditMixin

class Cliente(Base, AuditMixin):
    __tablename__ = "cliente"
    __table_args__ = {"schema": "public"}

    cliente_id = Column(Integer, primary_key=True, index=True)
    cliente_nombre = Column(String, nullable=False)
    cliente_email = Column(String, nullable=False)
    cliente_telefono = Column(String)
    cliente_empresa = Column(String)
    cliente_estado = Column(Boolean,default=True, nullable=False)  # activo / inactivo
