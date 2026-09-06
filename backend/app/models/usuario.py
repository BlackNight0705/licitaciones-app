from sqlalchemy import Boolean, Column, Integer, String
from .auditMixin import AuditMixin
from backend.app.core.database import Base

class Usuario(Base, AuditMixin):
    __tablename__ = "usuario"
    __table_args__ = {"schema": "public"}

    usuario_id = Column(Integer, primary_key=True, index=True)
    usuario_nombre = Column(String, nullable=False)
    usuario_email = Column(String, unique=True, nullable=False)
    usuario_hashed_password = Column(String, nullable=False)
    usuario_rol = Column(String, nullable=False)  # admin / user
    usuario_estado = Column(Boolean, default=True, nullable=False)  # activo / inactivo
