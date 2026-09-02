from sqlalchemy import Column, Integer,Boolean, String, Float, Date, ForeignKey
from sqlalchemy.orm import declarative_base
from .auditoria import AuditMixin

Base = declarative_base()

class Licitacion(Base, AuditMixin):
    __tablename__ = "licitacion"

    licitacion_id = Column(Integer, primary_key=True, index=True)

    licitacion_cliente_id = Column(Integer, ForeignKey("cliente.cliente_id"), nullable=False)
    licitacion_usuario_id = Column(Integer, ForeignKey("usuario.usuario_id"), nullable=False)

    licitacion_titulo = Column(String, nullable=False)
    licitacion_descripcion = Column(String)
    licitacion_presupuesto_maximo = Column(Float, nullable=False)
    licitacion_fecha_limite = Column(Date, nullable=False)
    licitacion_documento_url = Column(String)
    licitacion_estado = Column(String, nullable=False)  # borrador, activa, finalizada, por_cobrar, cobrada, perdida
    licitacion_cumple_requisitos = Column(Boolean, default=False)
    licitacion_aprobada_por_admin = Column(Boolean, default=False)
