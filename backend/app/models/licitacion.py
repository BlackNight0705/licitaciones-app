from sqlalchemy import Column, DateTime, Integer, Boolean, String, Float, Date, ForeignKey
from .auditoria import AuditMixin
from backend.app.core.database import Base
from sqlalchemy.orm import relationship

class Licitacion(Base, AuditMixin):
    __tablename__ = "licitacion"
    __table_args__ = {"schema": "public"}

    licitacion_id = Column(Integer, primary_key=True, index=True)

    licitacion_cliente_id = Column(Integer, ForeignKey("cliente.cliente_id"), nullable=False)
    licitacion_usuario_id = Column(Integer, ForeignKey("usuario.usuario_id"), nullable=False)

    cliente = relationship("Cliente", lazy="joined")
    productos = relationship("LicitacionProducto", backref="licitacion", cascade="all, delete-orphan")
    historial = relationship("HistorialTransicion", backref="licitacion", cascade="all, delete-orphan")

    licitacion_titulo = Column(String, nullable=False)
    licitacion_descripcion = Column(String)
    licitacion_presupuesto_maximo = Column(Float, nullable=False)
    licitacion_fecha_limite = Column(DateTime, nullable=False)
    licitacion_documento_url = Column(String)
    licitacion_estado = Column(String, nullable=False)  # borrador, activa, finalizada, por_cobrar, cobrada, perdida
    licitacion_cumple_requisitos = Column(Boolean, default=False)
    licitacion_aprobada_por_admin = Column(Boolean, default=False)