from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from backend.app.core.database import Base

class HistorialTransicion(Base):
    __tablename__ = "historial_transicion"
    __table_args__ = {"schema": "public"}

    historial_transicion_id = Column(Integer, primary_key=True, index=True)
    historial_transicion_licitacion_id = Column(Integer, ForeignKey("licitacion.licitacion_id"), nullable=False)

    historial_transicion_estado_anterior = Column(String, nullable=False)
    historial_transicion_estado_nuevo = Column(String, nullable=False)

    historial_transicion_usuario_id = Column(Integer, ForeignKey("usuario.usuario_id"), nullable=False)

    historial_transicion_fecha_transicion = Column(DateTime, default=datetime.utcnow, nullable=False)

    historial_transicion_fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    historial_transicion_fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

