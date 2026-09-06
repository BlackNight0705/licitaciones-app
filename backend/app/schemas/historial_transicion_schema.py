from pydantic import BaseModel, Field
from datetime import datetime

class HistorialTransicionBase(BaseModel):
    historial_transicion_estado_anterior: str = Field(
        ..., 
        min_length=1, 
        max_length=50, 
        description="El estado anterior no puede estar vacío."
    )
    historial_transicion_estado_nuevo: str = Field(
        ..., 
        min_length=1, 
        max_length=50, 
        description="El nuevo estado no puede estar vacío."
    )
    historial_transicion_usuario_id: int = Field(
        ..., 
        gt=0, 
        description="El ID del usuario debe ser mayor a 0."
    )

class HistorialTransicionCreate(HistorialTransicionBase):
    historial_transicion_licitacion_id: int = Field(
        ..., 
        gt=0, 
        description="El ID de la licitación debe ser mayor a 0."
    )

class HistorialTransicionResponse(HistorialTransicionBase):
    historial_transicion_id: int = Field(
        ..., 
        gt=0, 
        description="ID único del historial."
    )
    historial_transicion_fecha_transicion: datetime

    class Config:
        from_attributes = True