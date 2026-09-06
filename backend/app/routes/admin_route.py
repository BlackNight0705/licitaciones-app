from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.core.database import get_session
from backend.app.models.cliente import Cliente
from backend.app.models.usuario import Usuario
from backend.app.models.auditoria import AuditLog
from backend.app.core.security import obtener_usuario_actual

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