from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from pydantic import BaseModel, EmailStr

from backend.app.core.database import get_session
from backend.app.models.cliente import Cliente
from backend.app.models.usuario import Usuario
from backend.app.core.security import verificar_rol_admin, obtener_usuario_actual
from backend.app.models.auditoria import AuditLog

router = APIRouter(prefix="/cliente", tags=["Cliente"])

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

    await registrar_accion(
        session=session,
        usuario_id=admin_actual.usuario_id,
        accion="CREAR",
        modulo="Clientes",
        detalles=f"El administrador creó el cliente {nuevo_cliente.cliente_nombre}."
    )

    return nuevo_cliente

@router.get("/")
async def listar_clientes(
    session: AsyncSession = Depends(get_session),
    current_user: Usuario = Depends(obtener_usuario_actual)
):
    resultado = await session.execute(select(Cliente))
    clientes = resultado.scalars().all()

    await registrar_accion(
        session=session,
        usuario_id=current_user.usuario_id,
        accion="CONSULTA",
        modulo="Clientes",
        detalles=f"El usuario {current_user.usuario_email} consultó el listado de clientes."
    )

    return clientes