from sqlalchemy import Column, Integer, Float, Date, ForeignKey, String
from .auditoria import AuditMixin
from backend.app.core.database import Base

class Pago(Base, AuditMixin):
    __tablename__ = "pago"
    __table_args__ = {"schema": "public"}

    pago_id = Column(Integer, primary_key=True, index=True)
    pago_licitacion_id = Column(Integer, ForeignKey("licitacion.licitacion_id"), nullable=False)

    pago_monto = Column(Float, nullable=False)
    pago_fecha_pago = Column(Date, nullable=False)
    pago_metodo_pago = Column(String, default = "Tarjeta", nullable=False)

    pago_usuario_id = Column(Integer, ForeignKey("usuario.usuario_id"), nullable=False)
