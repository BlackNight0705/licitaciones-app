from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from .auditoria import AuditMixin

Base = declarative_base()

class Cliente(Base, AuditMixin):
    __tablename__ = "cliente"

    cliente_id = Column(Integer, primary_key=True, index=True)
    cliente_nombre = Column(String, nullable=False)
    cliente_email = Column(String, nullable=False)
    cliente_telefono = Column(String)
    cliente_empresa = Column(String)
