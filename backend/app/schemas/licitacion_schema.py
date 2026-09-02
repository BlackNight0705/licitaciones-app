from pydantic import BaseModel
from datetime import date

class LicitacionBase(BaseModel):
    licitacion_titulo: str
    licitacion_descripcion: str | None = None
    licitacion_presupuesto_maximo: float
    licitacion_fecha_limite: date
    licitacion_documento_url: str | None = None
    licitacion_estado: str

class LicitacionCreate(LicitacionBase):
    licitacion_cliente_id: int
    licitacion_usuario_id: int
class LicitacionResponse(LicitacionBase):
    licitacion_id: int
    licitacion_cumple_requisitos: bool
    licitacion_aprobada_por_admin: bool

    class Config:
        from_attributes = True
