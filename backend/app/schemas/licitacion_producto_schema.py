from typing import Optional
from pydantic import BaseModel, Field

from backend.app.schemas.producto_schema import ProductoResponse

class LicitacionProductoBase(BaseModel):
    cantidad: int = Field(
        ..., 
        gt=0, 
        description="La cantidad debe ser mayor a 0."
    )
    precio_unitario: float = Field(
        ..., 
        ge=0, 
        description="El precio unitario no puede ser negativo."
    )

class LicitacionProductoCreate(LicitacionProductoBase):
    nombre: str = Field(
        ..., 
        min_length=1, 
        max_length=150, 
        description="El nombre del producto no puede estar vacío."
    )

class LicitacionProductoResponse(BaseModel):
    id: int = Field(..., gt=0, alias="licitacion_producto_id")
    cantidad: int = Field(..., gt=0, alias="licitacion_producto_cantidad")
    precio_unitario: float = Field(..., ge=0, alias="licitacion_producto_precio_unitario")
    producto: Optional[ProductoResponse] = None

    class Config:
        populate_by_name = True
        from_attributes = True