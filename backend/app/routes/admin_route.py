from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from backend.app.core.database import get_session
from backend.app.models.cliente import Cliente
from backend.app.models.usuario import Usuario
from backend.app.models.auditoria import AuditLog
from backend.app.core.security import obtener_usuario_actual

router = APIRouter(prefix="/admin", tags=["Administración"])

# Dependencia para verificar que el usuario actual sea Administrador
async def verificar_rol_admin(current_user: Usuario = Depends(obtener_usuario_actual)):
    # Ajusta "usuario_rol" según el campo real de tu modelo de usuario
    if getattr(current_user, "usuario_rol", None) != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso exclusivo para administradores."
        )
    return current_user

# Función auxiliar para registrar eventos de auditoría desde cualquier parte del backend
async def registrar_accion(session: AsyncSession, usuario_id: int, accion: str, modulo: str, detalles: str):
    nuevo_log = AuditLog(
        usuario_id=usuario_id,
        accion=accion,
        modulo=modulo,
        detalles=detalles
    )
    session.add(nuevo_log)
    await session.commit()

# Endpoint para listar Usuarios y Clientes (solo admin)
@router.get("/usuarios")
async def obtener_todos_los_usuarios(
    session: AsyncSession = Depends(get_session),
    admin: Usuario = Depends(verificar_rol_admin)
):
    resultado = await session.execute(select(Usuario))
    usuarios = resultado.scalars().all()
    
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
    
    return [
        {
            "id": c.cliente_id,
            "nombre": c.cliente_nombre,
            # Agrega los campos que correspondan a tu modelo Cliente
        }
        for c in clientes
    ]

# Endpoint para ver la Bitácora de Auditoría (solo admin)
@router.get("/auditorias")
async def obtener_auditorias(
    session: AsyncSession = Depends(get_session),
    admin: Usuario = Depends(verificar_rol_admin)
):
    # Traemos los logs ordenados del más reciente al más antiguo
    resultado = await session.execute(
        select(AuditLog).order_by(AuditLog.fecha_hora.desc()).limit(100)
    )
    logs = resultado.scalars().all()
    
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