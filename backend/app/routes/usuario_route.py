from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.core.database import get_session
from backend.app.models.usuario import Usuario
from backend.app.core.security import verificar_rol_admin, obtener_password_hash
from pydantic import BaseModel, EmailStr
from backend.app.models.auditoria import AuditLog

router = APIRouter(prefix="/usuario", tags=["Usuario"])

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

class UsuarioCreate(BaseModel):
    usuario_nombre: str
    usuario_email: EmailStr
    usuario_password: str
    usuario_rol: str = "usuario"  # por defecto rol normal, o "admin"

#Crear un nuevo usuario (solo accesible para administradores)
@router.post("/", status_code=status.HTTP_201_CREATED)
async def crear_usuario(
    datos_usuario: UsuarioCreate,
    session: AsyncSession = Depends(get_session),
    admin_actual: Usuario = Depends(verificar_rol_admin)  # Solo entra si es admin
):
    # Verificar si el correo ya está registrado
    resultado = await session.execute(
        select(Usuario).where(Usuario.usuario_email == datos_usuario.usuario_email)
    )
    usuario_existente = resultado.scalars().first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado."
        )

    # Crear el hash de la contraseña de forma segura
    password_hashed = obtener_password_hash(datos_usuario.usuario_password)

    # Crear la instancia del nuevo usuario
    nuevo_usuario = Usuario(
        usuario_nombre=datos_usuario.usuario_nombre,
        usuario_email=datos_usuario.usuario_email,
        usuario_hashed_password=password_hashed,
        usuario_rol=datos_usuario.usuario_rol,
        entidad_creador_id=admin_actual.usuario_id
    )

    session.add(nuevo_usuario)
    await session.commit()
    await session.refresh(nuevo_usuario)

    return {
        "mensaje": "Usuario creado exitosamente",
        "usuario_id": nuevo_usuario.usuario_id,
        "usuario_email": nuevo_usuario.usuario_email
    }