from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_session
from app.schemas.pago_schema import PagoCreate, PagoResponse
from app.services.pago_service import registrar_pago
# Importa tu dependencia de usuario actual (ej. get_current_user)
# from app.core.security import get_current_user 

router = APIRouter(prefix="/pagos", tags=["Pagos"])

@router.post("/", response_model=PagoResponse)
async def registrar_pago_route(
    data: PagoCreate,
    session: AsyncSession = Depends(get_session),
    current_user = Depends() # Reemplaza por tu dependencia real de usuario autenticado
):
    # Si tienes el ID del usuario en el token, se lo pasas al servicio:
    usuario_id = getattr(current_user, "usuario_id", data.pago_usuario_id)
    return await registrar_pago(session, data, usuario_id)