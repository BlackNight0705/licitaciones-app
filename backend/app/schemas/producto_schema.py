from pydantic import BaseModel, Field

class ProductoBase(BaseModel):
    producto_nombre: str
    producto_descripcion: str | None = None
    producto_precio_unitario: float

class ProductoCreate(ProductoBase):
    pass

class ProductoResponse(BaseModel):
    producto_id: int
    nombre: str = Field(..., alias="producto_nombre")
    precio_unitario: float = Field(..., alias="producto_precio_unitario")

    class Config:
        populate_by_name = True
        from_attributes = True