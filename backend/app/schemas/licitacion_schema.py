from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel, Field, computed_field, field_validator

from backend.app.schemas.licitacion_producto_schema import LicitacionProductoResponse
from backend.app.schemas.historial_transicion_schema import HistorialTransicionResponse
from backend.app.schemas.pago_schema import PagoResponse

class ClienteShortResponse(BaseModel):
    cliente_id: int = Field(..., gt=0, description="ID único del cliente.")
    cliente_nombre: str = Field(..., min_length=1, max_length=150, description="Nombre del cliente.")

    class Config:
        from_attributes = True

class LicitacionBase(BaseModel):
    licitacion_titulo: str = Field(..., min_length=3, max_length=200, description="Título de la licitación.")
    licitacion_descripcion: Optional[str] = Field(None, max_length=1000, description="Descripción opcional.")
    licitacion_presupuesto_maximo: float = Field(..., gt=0, description="El presupuesto máximo debe ser mayor a 0.")
    licitacion_fecha_limite: datetime = Field(..., description="Fecha límite de la licitación.")
    licitacion_documento_url: Optional[str] = Field(None, max_length=500, description="URL del documento adjunto.")

class LicitacionCreate(LicitacionBase):
    licitacion_cliente_id: int = Field(..., gt=0, description="El ID del cliente asociado debe ser mayor a 0.")

    @field_validator("licitacion_fecha_limite")
    @classmethod
    def validar_fecha_no_pasada(cls, value: datetime | date) -> datetime | date:
        fecha_ingresada = value.date() if isinstance(value, datetime) else value
        if fecha_ingresada < date.today():
            raise ValueError("La fecha límite no puede ser anterior al día de hoy.")
        return value

class LicitacionResponse(LicitacionBase):
    licitacion_id: int = Field(..., gt=0)
    licitacion_estado: str = Field(..., min_length=1, max_length=50)
    licitacion_cliente_id: int = Field(..., gt=0)
    licitacion_cumple_requisitos: bool
    licitacion_aprobada_por_admin: bool
    cliente: Optional[ClienteShortResponse] = None

    class Config:
        from_attributes = True

class LicitacionDetailResponse(LicitacionResponse):
    productos: List[LicitacionProductoResponse] = []
    historial: List[HistorialTransicionResponse] = []
    pagos: List[PagoResponse] = []

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

class LicitacionUpdate(BaseModel):
    licitacion_titulo: Optional[str] = Field(None, min_length=3, max_length=200)
    licitacion_descripcion: Optional[str] = Field(None, max_length=1000)
    licitacion_presupuesto_maximo: Optional[float] = Field(None, gt=0)
    licitacion_fecha_limite: Optional[datetime] = Field(None, description="Fecha límite de la licitación.")
    licitacion_cliente_id: Optional[int] = Field(None, gt=0)
    licitacion_estado: Optional[str] = Field(None, min_length=1, max_length=50)