from pydantic import BaseModel
from typing import List
from datetime import datetime  # Asegúrate de importarlo correctamente aquí

from backend.app.schemas.licitacion_producto_schema import LicitacionProductoResponse
from backend.app.schemas.historial_transicion_schema import HistorialTransicionResponse

class ClienteShortResponse(BaseModel):
    cliente_id: int
    cliente_nombre: str  # Ajusta este campo si en tu modelo de cliente se llama diferente (ej: 'nombre')

    class Config:
        from_attributes = True

class LicitacionBase(BaseModel):
    licitacion_titulo: str
    licitacion_descripcion: str | None = None
    licitacion_presupuesto_maximo: float
    licitacion_fecha_limite: datetime
    licitacion_documento_url: str | None = None

class LicitacionCreate(LicitacionBase):
    licitacion_cliente_id: int

class LicitacionResponse(LicitacionBase):
    licitacion_id: int
    licitacion_estado: str 
    licitacion_cliente_id: int
    licitacion_cumple_requisitos: bool
    licitacion_aprobada_por_admin: bool
    cliente: ClienteShortResponse | None = None  # <-- Integrado para traer los datos del cliente/empresa

    class Config:
        from_attributes = True

class LicitacionDetailResponse(LicitacionResponse):
    productos: List[LicitacionProductoResponse] = []
    historial: List[HistorialTransicionResponse] = []

    class Config:
        from_attributes = True

class LicitacionUpdate(BaseModel):
    licitacion_titulo: str | None = None
    licitacion_descripcion: str | None = None
    licitacion_presupuesto_maximo: float | None = None
    licitacion_fecha_limite: datetime | None = None
    licitacion_cliente_id: int | None = None
    licitacion_estado: str | None = None