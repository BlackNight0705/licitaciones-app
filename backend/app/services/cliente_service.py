from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status

from backend.app.models.cliente import Cliente
from backend.app.models.auditoria import AuditLog
from backend.app.schemas.cliente_schema import ClienteCreate  # O tu archivo de esquemas correspondiente

async def registrar_accion(session: AsyncSession, usuario_id: int, accion: str, modulo: str, detalles: str):
    nuevo_log = AuditLog(
        usuario_id=usuario_id,
        accion=accion,
        modulo=modulo,
        detalles=detalles
    )
    session.add(nuevo_log)
    await session.commit()

async def service_crear_cliente(session: AsyncSession, datos: ClienteCreate, admin_id: int):
    nuevo_cliente = Cliente(
        cliente_nombre=datos.cliente_nombre,
        cliente_email=datos.cliente_email,
        cliente_telefono=datos.cliente_telefono,
        cliente_empresa=datos.cliente_empresa,
        entidad_creador_id=admin_id 
    )
    session.add(nuevo_cliente)
    await session.commit()
    await session.refresh(nuevo_cliente)

    await registrar_accion(
        session=session,
        usuario_id=admin_id,
        accion="CREAR",
        modulo="Clientes",
        detalles=f"El administrador creó el cliente {nuevo_cliente.cliente_nombre}."
    )

    return nuevo_cliente

async def service_listar_clientes(session: AsyncSession, current_user_id: int, current_user_email: str):
    resultado = await session.execute(select(Cliente))
    clientes = resultado.scalars().all()

    await registrar_accion(
        session=session,
        usuario_id=current_user_id,
        accion="CONSULTA",
        modulo="Clientes",
        detalles=f"El usuario {current_user_email} consultó el listado de clientes."
    )

    return clientes