from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from backend.app.models.usuario import Usuario
from backend.app.core.security import obtener_password_hash

async def crear_usuario_service(session: AsyncSession, datos_usuario, admin_id: int) -> Usuario:
    resultado = await session.execute(
        select(Usuario).where(Usuario.usuario_email == datos_usuario.usuario_email)
    )
    usuario_existente = resultado.scalars().first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado."
        )

    password_hashed = obtener_password_hash(datos_usuario.usuario_password)

    nuevo_usuario = Usuario(
        usuario_nombre=datos_usuario.usuario_nombre,
        usuario_email=datos_usuario.usuario_email,
        usuario_hashed_password=password_hashed,
        usuario_rol=datos_usuario.usuario_rol,
        entidad_creador_id=admin_id
    )

    session.add(nuevo_usuario)
    await session.commit()
    await session.refresh(nuevo_usuario)
    return nuevo_usuario