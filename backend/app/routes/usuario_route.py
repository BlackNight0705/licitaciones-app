from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_session
from backend.app.models.usuario import Usuario
from backend.app.core.security import verificar_rol_admin
from pydantic import BaseModel, EmailStr
from backend.app.models.auditoria import AuditLog
from backend.app.services.user_service import crear_usuario_service

router = APIRouter(prefix="/usuario", tags=["Usuario"])

async def registrar_accion(session: AsyncSession, usuario_id: int, accion: str, modulo: str, detalles: str):
    nuevo_log = AuditLog(
        usuario_id=usuario_id,
        accion=accion,
        modulo=modulo,
        detalles=detalles
    )
    session.add(nuevo_log)
    await session.commit()

class UsuarioCreate(BaseModel):
    usuario_nombre: str
    usuario_email: EmailStr
    usuario_password: str
    usuario_rol: str = "usuario"

@router.post("/", status_code=status.HTTP_201_CREATED)
async def crear_usuario_route(
    datos_usuario: UsuarioCreate,
    session: AsyncSession = Depends(get_session),
    admin_actual: Usuario = Depends(verificar_rol_admin)
):
    nuevo_usuario = await crear_usuario_service(session, datos_usuario, admin_actual.usuario_id)

    await registrar_accion(
        session=session,
        usuario_id=admin_actual.usuario_id,
        accion="CREAR",
        modulo="Usuarios",
        detalles=f"El administrador creó el usuario {nuevo_usuario.usuario_email} con rol {nuevo_usuario.usuario_rol}."
    )

    return {
        "mensaje": "Usuario creado exitosamente",
        "usuario_id": nuevo_usuario.usuario_id,
        "usuario_email": nuevo_usuario.usuario_email
    }