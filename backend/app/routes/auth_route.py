from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.core.database import get_session
from backend.app.models.usuario import Usuario
from backend.app.core.security import verificar_password, crear_access_token, decodificar_token
from backend.app.models.auditoria import AuditLog 

router = APIRouter(tags=["Autenticación"])

async def registrar_accion(session: AsyncSession, usuario_id: int, accion: str, modulo: str, detalles: str):
    nuevo_log = AuditLog(
        usuario_id=usuario_id,
        accion=accion,
        modulo=modulo,
        detalles=detalles
    )
    session.add(nuevo_log)
    await session.commit()

@router.post("/login")
async def login(
    response: Response,  # <--- 1. Inyectamos el objeto Response de FastAPI
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    resultado = await session.execute(
        select(Usuario).where(Usuario.usuario_email == form_data.username)
    )
    usuario = resultado.scalars().first()

    if not usuario or not verificar_password(form_data.password, usuario.usuario_hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 1. Creamos el Access Token (corto: 2 a 15 minutos)
    access_token_expires = timedelta(minutes=15)
    access_token = crear_access_token(data={"sub": str(usuario.usuario_id)}, expires_delta=access_token_expires)

    # 2. Creamos el Refresh Token (largo: 7 días)
    refresh_token_expires = timedelta(days=7)
    refresh_token = crear_access_token(data={"sub": str(usuario.usuario_id)}, expires_delta=refresh_token_expires)

    # <--- 2. Guardamos ambos en cookies HttpOnly separadas
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True, 
        samesite="none",
        max_age=900 
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=604800 
    )

    await registrar_accion(
        session=session,
        usuario_id=usuario.usuario_id,
        accion="LOGIN",
        modulo="Autenticación",
        detalles=f"El usuario {usuario.usuario_email} inició sesión exitosamente."
    )

    # <--- 3. Devolvemos solo los datos informativos del usuario
    return {
        "mensaje": "Login exitoso",
        "usuario_id": usuario.usuario_id,
        "usuario_email": usuario.usuario_email,
        "usuario_rol": usuario.usuario_rol
    }

@router.post("/auth/refresh")
async def refresh_token(
    response: Response,  # <--- 1. Inyectamos la instancia de Response correctamente
    refresh_token: str = Cookie(None), # <---- Leemos la cookie del refresh token directamente
    session: AsyncSession = Depends(get_session)
):
    """
    Renueva el access token usando el refresh token almacenado de forma segura.
    """
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No se encontró el token de actualización"
        )

    try:
        # Decodificamos el refresh token para obtener el ID del usuario
        payload = decodificar_token(refresh_token) 
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Token inválido")
    except Exception:
        raise HTTPException(status_code=401, detail="Token de actualización expirado o inválido")

    # Verificamos que el usuario siga existiendo en la base de datos
    resultado = await session.execute(select(Usuario).where(Usuario.usuario_id == int(user_id)))
    usuario = resultado.scalars().first()
    
    if not usuario:
        raise HTTPException(status_code=401, detail="Usuario no encontrado")

    # Generamos un nuevo Access Token fresco
    access_token_expires = timedelta(minutes=15)
    nuevo_access_token = crear_access_token(
        data={"sub": str(usuario.usuario_id)}, 
        expires_delta=access_token_expires
    )
    
    # <--- 2. Actualizamos la cookie HttpOnly con el nuevo token fresco
    response.set_cookie(
        key="access_token",
        value=nuevo_access_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=900
    )
    
    await registrar_accion(
        session=session,
        usuario_id=usuario.usuario_id,
        accion="REFRESH",
        modulo="Autenticación",
        detalles=f"Se renovó el token de acceso para el usuario {usuario.usuario_email}."
    )

    return {
        "mensaje": "Token renovado exitosamente",
        "usuario_id": usuario.usuario_id,
        "usuario_email": usuario.usuario_email
    }

@router.post("/logout")
async def logout(response: Response):
    # Borramos la cookie del access_token sobrescribiéndola vacía y expirada
    response.delete_cookie(key="access_token", samesite="none", secure=True)
    
    # Borramos también el refresh_token
    response.delete_cookie(key="refresh_token", samesite="none", secure=True)
    
    return {"mensaje": "Sesión cerrada exitosamente"}