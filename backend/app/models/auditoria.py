from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from backend.app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuario.usuario_id"), nullable=True)
    accion = Column(String(100), nullable=False)  # Ej: "LOGIN", "CREAR_LICITACION", "ELIMINAR_PRODUCTO"
    modulo = Column(String(50), nullable=False)   # Ej: "Autenticación", "Licitaciones", "Finanzas"
    detalles = Column(Text, nullable=True)        # Descripción legible de lo ocurrido
    fecha_hora = Column(DateTime(timezone=True), server_default=func.now())