from typing import Optional
from pydantic import BaseModel, Field

from backend.app.schemas.producto_schema import ProductoResponse

class LicitacionProductoBase(BaseModel):
    cantidad: int
    precio_unitario: float

class LicitacionProductoCreate(LicitacionProductoBase):
    nombre: str

class LicitacionProductoResponse(BaseModel):
    id: int = Field(..., alias="licitacion_producto_id")
    cantidad: int = Field(..., alias="licitacion_producto_cantidad")
    precio_unitario: float = Field(..., alias="licitacion_producto_precio_unitario")
    producto: Optional[ProductoResponse] = None

    class Config:
        populate_by_name = True
        from_attributes = True