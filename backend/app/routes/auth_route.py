from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.core.database import get_session
from backend.app.models.usuario import Usuario
from backend.app.core.security import verificar_password, crear_access_token, decodificar_token # Asegúrate de tener una función para decodificar/verificar tokens
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
    response: Response, 
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

    # 3. Guardamos ambos en cookies HttpOnly separadas
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True, # True en producción con HTTPS, False en local si no usas HTTPS
        samesite="none",
        max_age=900 # 15 minutos en segundos
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=604800 # 7 días en segundos
    )

    return {
        "mensaje": "Login exitoso",
        "usuario_id": usuario.usuario_id,
        "usuario_email": usuario.usuario_email,
        "usuario_rol": usuario.usuario_rol
    }

@router.post("/auth/refresh")
async def refresh_token(
    response: Response,  
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
        payload = decodificar_token(refresh_token) # Función que valida la firma del token
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
    
    # Actualizamos únicamente la cookie del access_token
    response.set_cookie(
        key="access_token",
        value=nuevo_access_token,
        httponly=True,
        secure=True,
        samesite="none",
        max_age=900
    )
    
    return {
        "mensaje": "Token renovado exitosamente",
        "usuario_id": usuario.usuario_id,
        "usuario_email": usuario.usuario_email
    }