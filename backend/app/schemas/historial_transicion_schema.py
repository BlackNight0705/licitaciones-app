from pydantic import BaseModel
from datetime import datetime

class HistorialTransicionBase(BaseModel):
    historial_transicion_estado_anterior: str
    historial_transicion_estado_nuevo: str
    historial_transicion_usuario_id: int

class HistorialTransicionCreate(HistorialTransicionBase):
    historial_transicion_licitacion_id: int

class HistorialTransicionResponse(HistorialTransicionBase):
    historial_transicion_id: int
    historial_transicion_fecha_transicion: datetime

    class Config:
        from_attributes = True
