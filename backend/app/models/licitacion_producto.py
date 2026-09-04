from sqlalchemy import Column, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from .auditoria import AuditMixin
from backend.app.core.database import Base
from backend.app.models.producto import Producto  # <--- Importa la clase Producto aquí

class LicitacionProducto(Base, AuditMixin):
    __tablename__ = "licitacion_producto"
    __table_args__ = {"schema": "public"}

    licitacion_producto_id = Column(Integer, primary_key=True, index=True)

    licitacion_producto_licitacion_id = Column(Integer, ForeignKey("licitacion.licitacion_id"), nullable=False)
    licitacion_producto_producto_id = Column(Integer, ForeignKey("producto.producto_id"), nullable=False)

    licitacion_producto_cantidad = Column(Integer, nullable=False)
    licitacion_producto_precio_unitario = Column(Float, nullable=False)

    # Relación directa usando la clase importada para evitar errores de búsqueda por nombre
    producto = relationship(Producto, lazy="joined")