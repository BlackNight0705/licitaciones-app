from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_session
from backend.app.core.security import obtener_usuario_actual
from backend.app.models.usuario import Usuario
from backend.app.schemas.pago_schema import PagoCreate, PagoResponse
from backend.app.services.pago_service import registrar_pago
from backend.app.models.auditoria import AuditLog

router = APIRouter(prefix="/pagos", tags=["Pagos"])

# Función auxiliar interna para registrar logs fácilmente
async def registrar_accion(session: AsyncSession, usuario_id: int, accion: str, modulo: str, detalles: str):
    nuevo_log = AuditLog(
        usuario_id=usuario_id,
        accion=accion,
        modulo=modulo,
        detalles=detalles
    )
    session.add(nuevo_log)
    await session.commit()

@router.post("/", response_model=PagoResponse)
async def registrar_pago_route(
    data: PagoCreate,
    session: AsyncSession = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    pago = await registrar_pago(session, data, usuario_actual.usuario_id)
    
    await registrar_accion(
        session=session,
        usuario_id=usuario_actual.usuario_id,
        accion="CREAR",
        modulo="Pagos",
        detalles=f"El usuario registró un nuevo pago asociado a la licitación o concepto correspondiente."
    )
    
    return pago