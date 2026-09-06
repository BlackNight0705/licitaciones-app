from pydantic import BaseModel, Field
from typing import Optional

class ProductoBase(BaseModel):
    producto_nombre: str = Field(
        ..., 
        min_length=1, 
        max_length=150, 
        description="El nombre del producto no puede estar vacío."
    )
    producto_descripcion: Optional[str] = Field(
        None, 
        max_length=500, 
        description="Descripción opcional del producto."
    )
    producto_precio_unitario: float = Field(
        ..., 
        ge=0, 
        description="El precio unitario no puede ser negativo."
    )

class ProductoCreate(ProductoBase):
    pass

class ProductoResponse(BaseModel):
    producto_id: int = Field(
        ..., 
        gt=0, 
        description="ID único del producto."
    )
    nombre: str = Field(
        ..., 
        min_length=1, 
        max_length=150, 
        alias="producto_nombre"
    )
    precio_unitario: float = Field(
        ..., 
        ge=0, 
        alias="producto_precio_unitario"
    )

    class Config:
        populate_by_name = True
        from_attributes = True