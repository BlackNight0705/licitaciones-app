from pydantic import BaseModel, Field
from datetime import date
from typing import Optional

class PagoBase(BaseModel):
    pago_monto: float = Field(
        ..., 
        gt=0, 
        description="El monto del pago debe ser estrictamente mayor a 0."
    )
    pago_fecha_pago: Optional[date] = Field(
        None, 
        description="Fecha opcional en que se realizó el pago."
    )
    pago_metodo_pago: str = Field(
        "tarjeta", 
        min_length=1, 
        max_length=50, 
        description="Método de pago utilizado."
    )

class PagoCreate(PagoBase):
    pago_licitacion_id: int = Field(
        ..., 
        gt=0, 
        description="El ID de la licitación debe ser mayor a 0."
    )
    pago_usuario_id: Optional[int] = Field(
        None, 
        gt=0, 
        description="El ID del usuario debe ser mayor a 0 si se especifica."
    )

class PagoResponse(PagoBase):
    pago_id: int = Field(
        ..., 
        gt=0, 
        description="ID único del pago registrado."
    )

    class Config:
        from_attributes = True