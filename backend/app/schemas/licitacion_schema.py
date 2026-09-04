from pydantic import BaseModel, computed_field
from typing import List
from datetime import datetime  # Asegúrate de importarlo correctamente aquí

from backend.app.schemas.licitacion_producto_schema import LicitacionProductoResponse
from backend.app.schemas.historial_transicion_schema import HistorialTransicionResponse
from backend.app.schemas.pago_schema import PagoResponse

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
    pagos: List[PagoResponse] = []  # <--- Añades esto

    @computed_field
    @property
    def total_pagado(self) -> float:
        if not self.pagos:
            return 0.0
        return sum(p.pago_monto for p in self.pagos)

    @computed_field
    @property
    def saldo_pendiente(self) -> float:
        presupuesto = self.licitacion_presupuesto_maximo or 0.0
        return max(0.0, presupuesto - self.total_pagado)

    class Config:
        from_attributes = True

    class Config:
        from_attributes = True

class LicitacionUpdate(BaseModel):
    licitacion_titulo: str | None = None
    licitacion_descripcion: str | None = None
    licitacion_presupuesto_maximo: float | None = None
    licitacion_fecha_limite: datetime | None = None
    licitacion_cliente_id: int | None = None
    licitacion_estado: str | None = None