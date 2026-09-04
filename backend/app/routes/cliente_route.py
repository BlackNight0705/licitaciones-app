from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from pydantic import BaseModel, EmailStr

from backend.app.core.database import get_session
from backend.app.models.cliente import Cliente
from backend.app.models.usuario import Usuario
from backend.app.core.security import verificar_rol_admin

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
    nuevo_cliente = Cliente(
        cliente_nombre=datos.cliente_nombre,
        cliente_email=datos.cliente_email,
        cliente_telefono=datos.cliente_telefono,
        cliente_empresa=datos.cliente_empresa,
        entidad_creador_id=admin_actual.usuario_id 
    )
    session.add(nuevo_cliente)
    await session.commit()
    await session.refresh(nuevo_cliente)
    return nuevo_cliente

@router.get("/")
async def listar_clientes(session: AsyncSession = Depends(get_session)):
    resultado = await session.execute(select(Cliente))
    return resultado.scalars().all()