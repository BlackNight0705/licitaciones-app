from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base
from .auditoria import AuditMixin

Base = declarative_base()

class Producto(Base, AuditMixin):
    __tablename__ = "producto"

    producto_id = Column(Integer, primary_key=True, index=True)
    producto_nombre = Column(String, nullable=False)
    producto_descripcion = Column(String)
    producto_precio_unitario = Column(Float, nullable=False)
