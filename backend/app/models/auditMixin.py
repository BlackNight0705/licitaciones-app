from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, ForeignKey

class AuditMixin:
    entidad_fecha_creacion = Column(DateTime, default=datetime.utcnow, nullable=False)
    entidad_fecha_actualizacion = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    entidad_creador_id = Column(Integer, ForeignKey("usuario.usuario_id"), nullable=False) 
    entidad_modificador_id = Column(Integer, ForeignKey("usuario.usuario_id"))
