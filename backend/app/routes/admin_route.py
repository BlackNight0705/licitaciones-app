from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
from pydantic import BaseModel, EmailStr

from backend.app.core.database import get_session
from backend.app.models.cliente import Cliente
from backend.app.models.usuario import Usuario
from backend.app.models.auditoria import AuditLog
from backend.app.core.security import obtener_usuario_actual, obtener_password_hash

router = APIRouter(prefix="/admin", tags=["Administración"])

async def verificar_rol_admin(current_user: Usuario = Depends(obtener_usuario_actual)):
    if getattr(current_user, "usuario_rol", None) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso exclusivo para administradores."
        )
    return current_user

async def registrar_accion(session: AsyncSession, usuario_id: int, accion: str, modulo: str, detalles: str):
    nuevo_log = AuditLog(
        usuario_id=usuario_id,
        accion=accion,
        modulo=modulo,
        detalles=detalles
    )
    session.add(nuevo_log)
    await session.commit()

class UsuarioUpdateAdmin(BaseModel):
    usuario_nombre: Optional[str] = None
    usuario_email: Optional[EmailStr] = None
    usuario_password: Optional[str] = None
    usuario_rol: Optional[str] = None

class ClienteUpdateAdmin(BaseModel):
    cliente_nombre: Optional[str] = None
    cliente_email: Optional[EmailStr] = None
    cliente_telefono: Optional[str] = None
    cliente_empresa: Optional[str] = None

@router.get("/usuarios")
async def obtener_todos_los_usuarios(
    session: AsyncSession = Depends(get_session),
    admin: Usuario = Depends(verificar_rol_admin)
):
    resultado = await session.execute(select(Usuario))
    usuarios = resultado.scalars().all()
    
    await registrar_accion(
        session=session,
        usuario_id=admin.usuario_id,
        accion="CONSULTA",
        modulo="Usuarios",
        detalles="El administrador consultó el listado completo de usuarios del sistema."
    )
    
    return [
        {
            "id": u.usuario_id,
            "nombre": u.usuario_nombre,
            "email": u.usuario_email,
            "rol": u.usuario_rol
        }
        for u in usuarios
    ]

@router.put("/usuarios/{usuario_id}")
async def actualizar_usuario_admin(
    usuario_id: int,
    datos: UsuarioUpdateAdmin,
    session: AsyncSession = Depends(get_session),
    admin: Usuario = Depends(verificar_rol_admin)
):
    resultado = await session.execute(select(Usuario).where(Usuario.usuario_id == usuario_id))
    usuario = resultado.scalars().first()
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if datos.usuario_nombre is not None:
        usuario.usuario_nombre = datos.usuario_nombre
    if datos.usuario_email is not None:
        usuario.usuario_email = datos.usuario_email
    if datos.usuario_rol is not None:
        usuario.usuario_rol = datos.usuario_rol
    if datos.usuario_password is not None:
        usuario.usuario_hashed_password = obtener_password_hash(datos.usuario_password)

    await session.commit()
    await session.refresh(usuario)

    await registrar_accion(
        session=session,
        usuario_id=admin.usuario_id,
        accion="ACTUALIZAR",
        modulo="Usuarios",
        detalles=f"El administrador actualizó los datos del usuario ID {usuario_id} ({usuario.usuario_email})."
    )

    return {"mensaje": "Usuario actualizado exitosamente", "usuario_id": usuario.usuario_id}

@router.delete("/usuarios/{usuario_id}", status_code=status.HTTP_200_OK)
async def eliminar_usuario_admin(
    usuario_id: int,
    session: AsyncSession = Depends(get_session),
    admin: Usuario = Depends(verificar_rol_admin)
):
    if usuario_id == admin.usuario_id:
        raise HTTPException(status_code=400, detail="No puedes eliminar tu propia cuenta de administrador.")

    resultado = await session.execute(select(Usuario).where(Usuario.usuario_id == usuario_id))
    usuario = resultado.scalars().first()

    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    email_eliminado = usuario.usuario_email
    await session.delete(usuario)
    await session.commit()

    await registrar_accion(
        session=session,
        usuario_id=admin.usuario_id,
        accion="ELIMINAR",
        modulo="Usuarios",
        detalles=f"El administrador eliminó al usuario ID {usuario_id} ({email_eliminado})."
    )

    return {"mensaje": f"Usuario {email_eliminado} eliminado exitosamente"}

@router.get("/clientes")
async def obtener_todos_los_clientes(
    session: AsyncSession = Depends(get_session),
    admin: Usuario = Depends(verificar_rol_admin)
):
    resultado = await session.execute(select(Cliente))
    clientes = resultado.scalars().all()
    
    await registrar_accion(
        session=session,
        usuario_id=admin.usuario_id,
        accion="CONSULTA",
        modulo="Clientes",
        detalles="El administrador consultó el listado completo de clientes del sistema."
    )
    
    return [
        {
            "id": c.cliente_id,
            "nombre": c.cliente_nombre,
        }
        for c in clientes
    ]

@router.put("/clientes/{cliente_id}")
async def actualizar_cliente_admin(
    cliente_id: int,
    datos: ClienteUpdateAdmin,
    session: AsyncSession = Depends(get_session),
    admin: Usuario = Depends(verificar_rol_admin)
):
    resultado = await session.execute(select(Cliente).where(Cliente.cliente_id == cliente_id))
    cliente = resultado.scalars().first()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    if datos.cliente_nombre is not None:
        cliente.cliente_nombre = datos.cliente_nombre
    if datos.cliente_email is not None:
        cliente.cliente_email = datos.cliente_email
    if datos.cliente_telefono is not None:
        cliente.cliente_telefono = datos.cliente_telefono
    if datos.cliente_empresa is not None:
        cliente.cliente_empresa = datos.cliente_empresa

    await session.commit()
    await session.refresh(cliente)

    await registrar_accion(
        session=session,
        usuario_id=admin.usuario_id,
        accion="ACTUALIZAR",
        modulo="Clientes",
        detalles=f"El administrador actualizó los datos del cliente ID {cliente_id}."
    )

    return {"mensaje": "Cliente actualizado exitosamente", "cliente_id": cliente.cliente_id}

@router.delete("/clientes/{cliente_id}", status_code=status.HTTP_200_OK)
async def eliminar_cliente_admin(
    cliente_id: int,
    session: AsyncSession = Depends(get_session),
    admin: Usuario = Depends(verificar_rol_admin)
):
    resultado = await session.execute(select(Cliente).where(Cliente.cliente_id == cliente_id))
    cliente = resultado.scalars().first()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente no encontrado")

    nombre_cliente = getattr(cliente, "cliente_nombre", "Desconocido")
    await session.delete(cliente)
    await session.commit()

    await registrar_accion(
        session=session,
        usuario_id=admin.usuario_id,
        accion="ELIMINAR",
        modulo="Clientes",
        detalles=f"El administrador eliminó al cliente ID {cliente_id} ({nombre_cliente})."
    )

    return {"mensaje": f"Cliente {nombre_cliente} eliminado exitosamente"}

@router.get("/auditorias")
async def obtener_auditorias(
    session: AsyncSession = Depends(get_session),
    admin: Usuario = Depends(verificar_rol_admin)
):
    resultado = await session.execute(
        select(AuditLog).order_by(AuditLog.fecha_hora.desc()).limit(100)
    )
    logs = resultado.scalars().all()
    
    await registrar_accion(
        session=session,
        usuario_id=admin.usuario_id,
        accion="CONSULTA",
        modulo="Auditoría",
        detalles="El administrador consultó la bitácora de auditoría del sistema."
    )
    
    return [
        {
            "id": log.id,
            "usuario_id": log.usuario_id,
            "accion": log.accion,
            "modulo": log.modulo,
            "detalles": log.detalles,
            "fecha_hora": log.fecha_hora
        }
        for log in logs
    ]