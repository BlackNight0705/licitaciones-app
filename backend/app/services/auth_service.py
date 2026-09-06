from datetime import timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.models.usuario import Usuario
from backend.app.models.auditoria import AuditLog
from backend.app.core.security import verificar_password, crear_access_token, decodificar_token

async def registrar_accion(session: AsyncSession, usuario_id: int, accion: str, modulo: str, detalles: str):
    nuevo_log = AuditLog(
        usuario_id=usuario_id,
        accion=accion,
        modulo=modulo,
        detalles=detalles
    )
    session.add(nuevo_log)
    await session.commit()

async def service_login(session: AsyncSession, email: str, password: str):
    resultado = await session.execute(
        select(Usuario).where(Usuario.usuario_email == email)
    )
    usuario = resultado.scalars().first()

    if not usuario or not verificar_password(password, usuario.usuario_hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=15)
    access_token = crear_access_token(data={"sub": str(usuario.usuario_id)}, expires_delta=access_token_expires)

    refresh_token_expires = timedelta(days=7)
    refresh_token = crear_access_token(data={"sub": str(usuario.usuario_id)}, expires_delta=refresh_token_expires)

    await registrar_accion(
        session=session,
        usuario_id=usuario.usuario_id,
        accion="LOGIN",
        modulo="Autenticación",
        detalles=f"El usuario {usuario.usuario_email} inició sesión exitosamente."
    )

    return {
        "usuario": usuario,
        "access_token": access_token,
        "refresh_token": refresh_token
    }

async def service_refresh_token(session: AsyncSession, refresh_token_str: str):
    if not refresh_token_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se encontró el token de actualización"
        )

    try:
        payload = decodificar_token(refresh_token_str) 
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token inválido")
    except Exception:
        raise HTTPException(status_code=401, detail="Token de actualización expirado o inválido")

    resultado = await session.execute(select(Usuario).where(Usuario.usuario_id == int(user_id)))
    usuario = resultado.scalars().first()
    
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    access_token_expires = timedelta(minutes=15)
    nuevo_access_token = crear_access_token(
        data={"sub": str(usuario.usuario_id)}, 
        expires_delta=access_token_expires
    )
    
    await registrar_accion(
        session=session,
        usuario_id=usuario.usuario_id,
        accion="REFRESH",
        modulo="Autenticación",
        detalles=f"Se renovó el token de acceso para el usuario {usuario.usuario_email}."
    )

    return {
        "usuario": usuario,
        "nuevo_access_token": nuevo_access_token
    }