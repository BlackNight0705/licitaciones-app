# services/auth_service.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status

from backend.app.models.usuario import Usuario
from backend.app.core.security import verificar_password, crear_access_token

async def autenticar_usuario(session: AsyncSession, email: str, password_plana: str):
    result = await session.execute(
        select(Usuario).where(Usuario.usuario_email == email)
    )
    usuario = result.scalars().first()

    if not usuario or not verificar_password(password_plana, usuario.usuario_hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = crear_access_token(data={"sub": str(usuario.usuario_id), "rol": usuario.usuario_rol})
    return {"access_token": access_token, "token_type": "bearer"}