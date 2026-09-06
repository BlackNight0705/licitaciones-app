from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pydantic import BaseModel, EmailStr

from backend.app.core.database import get_session
from backend.app.models.usuario import Usuario
from backend.app.core.security import verificar_rol_admin, obtener_usuario_actual
from backend.app.services.cliente_service import service_crear_cliente, service_listar_clientes

router = APIRouter(prefix="/cliente", tags=["Cliente"])

class ClienteCreate(BaseModel):
    cliente_nombre: str
    cliente_email: EmailStr
    cliente_telefono: Optional[str] = None
    cliente_empresa: Optional[str] = None

@router.post("/", status_code=status.HTTP_201_CREATED)
async def crear_cliente(
    datos: ClienteCreate,
    session: AsyncSession = Depends(get_session),
    admin_actual: Usuario = Depends(verificar_rol_admin)
):
    return await service_crear_cliente(session, datos, admin_actual.usuario_id)

@router.get("/")
async def listar_clientes(
    session: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(obtener_usuario_actual)
):
    return await service_listar_clientes(session, current_user.usuario_id, current_user.usuario_email)