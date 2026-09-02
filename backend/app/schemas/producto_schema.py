from pydantic import BaseModel

class ProductoBase(BaseModel):
    producto_nombre: str
    producto_descripcion: str | None = None
    producto_precio_unitario: float

class ProductoCreate(ProductoBase):
    pass

class ProductoResponse(ProductoBase):
    producto_id: int

    class Config:
        from_attributes = True
