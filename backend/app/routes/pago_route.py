from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_session
from backend.app.schemas.pago_schema import PagoCreate, PagoResponse
from backend.app.services.pago_service import registrar_pago

router = APIRouter(prefix="/pagos", tags=["Pagos"])

@router.post("/", response_model=PagoResponse)
async def registrar_pago_route(
    data: PagoCreate,
    session: AsyncSession = Depends(get_session)
):
    return await registrar_pago(session, data)
