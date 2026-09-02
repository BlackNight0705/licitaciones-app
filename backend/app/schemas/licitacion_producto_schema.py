from pydantic import BaseModel

class LicitacionProductoBase(BaseModel):
    licitacion_producto_cantidad: int
    licitacion_producto_precio_unitario: float

class LicitacionProductoCreate(LicitacionProductoBase):
    licitacion_producto_licitacion_id: int
    licitacion_producto_producto_id: int

class LicitacionProductoResponse(LicitacionProductoBase):
    licitacion_producto_id: int

    class Config:
        from_attributes = True
