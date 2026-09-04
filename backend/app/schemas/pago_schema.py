from pydantic import BaseModel
from datetime import date
from typing import Optional

class PagoBase(BaseModel):
    pago_monto: float
    pago_fecha_pago: Optional[date] = None
    pago_metodo_pago: str = "tarjeta"

class PagoCreate(PagoBase):
    pago_licitacion_id: int
    pago_usuario_id: Optional[int] = None

class PagoResponse(PagoBase):
    pago_id: int

    class Config:
        from_attributes = True