from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from .auditoria import AuditMixin

Base = declarative_base()

class Usuario(Base, AuditMixin):
    __tablename__ = "usuario"

    usuario_id = Column(Integer, primary_key=True, index=True)
    usuario_nombre = Column(String, nullable=False)
    usuario_email = Column(String, unique=True, nullable=False)
    usuario_hashed_password = Column(String, nullable=False)
    usuario_rol = Column(String, nullable=False)  # admin / user
