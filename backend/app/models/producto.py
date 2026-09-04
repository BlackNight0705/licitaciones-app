from sqlalchemy import Column, Integer, String, Float
from .auditoria import AuditMixin
from backend.app.core.database import Base

class Producto(Base, AuditMixin):
    __tablename__ = "producto"
    __table_args__ = {"schema": "public"}

    producto_id = Column(Integer, primary_key=True, index=True)
    producto_nombre = Column(String, nullable=False)
    producto_descripcion = Column(String)
    producto_precio_unitario = Column(Float, nullable=False)
