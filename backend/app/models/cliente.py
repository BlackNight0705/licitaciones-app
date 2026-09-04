from sqlalchemy import Column, Integer, String
from backend.app.core.database import Base
from .auditoria import AuditMixin

class Cliente(Base, AuditMixin):
    __tablename__ = "cliente"
    __table_args__ = {"schema": "public"}

    cliente_id = Column(Integer, primary_key=True, index=True)
    cliente_nombre = Column(String, nullable=False)
    cliente_email = Column(String, nullable=False)
    cliente_telefono = Column(String)
    cliente_empresa = Column(String)
