from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import declarative_base
from .auditoria import AuditMixin

Base = declarative_base()

class LicitacionProducto(Base, AuditMixin):
    __tablename__ = "licitacion_producto"

    licitacion_producto_id = Column(Integer, primary_key=True, index=True)

    licitacion_producto_licitacion_id = Column(Integer, ForeignKey("licitacion.licitacion_id"), nullable=False)
    licitacion_producto_producto_id = Column(Integer, ForeignKey("producto.producto_id"), nullable=False)

    licitacion_producto_cantidad = Column(Integer, nullable=False)
    licitacion_producto_precio_unitario = Column(Float, nullable=False)
