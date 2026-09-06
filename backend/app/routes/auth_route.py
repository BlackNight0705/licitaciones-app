from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.core.database import get_session
from backend.app.models.usuario import Usuario
from backend.app.core.security import obtener_usuario_actual, verificar_password, crear_access_token
from backend.app.models.auditoria import AuditLog 

router = APIRouter(tags=["Autenticación"])

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

    access_token = crear_access_token(data={"sub": str(usuario.usuario_id)})

    # <--- 2. Guardamos el token de forma segura en una cookie HttpOnly
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,       # False para pruebas locales en HTTP, True en producción con HTTPS
        samesite="none",
        max_age=120       # Tiempo de expiración en segundos (30 min)
    )

    # <--- 3. Devolvemos solo los datos informativos del usuario (el token ya viaja oculto en la cookie)
    return {
        "mensaje": "Login exitoso",
        "usuario_id": usuario.usuario_id,
        "usuario_email": usuario.usuario_email,
        "usuario_rol": usuario.usuario_rol
    }

@router.post("/auth/refresh")
async def refresh_token(
    response: Response,  # <--- 1. Inyectamos la instancia de Response correctamente
    current_user: Usuario = Depends(obtener_usuario_actual)
):
    """
    Renueva el token de acceso y lo actualiza en la cookie HttpOnly.
    """
    # 30 minutos de expiración en segundos para el max_age (30 * 60 = 1800)
    access_token_expires = timedelta(minutes=2)
    
    # Mantenemos la misma estructura del login usando el id del usuario en "sub"
    nuevo_token = crear_access_token(
        data={"sub": str(current_user.usuario_id)}, 
        expires_delta=access_token_expires
    )
    
    # <--- 2. Actualizamos la cookie HttpOnly con el nuevo token fresco
    response.set_cookie(
        key="access_token",
        value=nuevo_token,
        httponly=True,
        secure=True,      # Cambiar a False si pruebas en local sin HTTPS, True en producción
        samesite="none",
        max_age=1800      # 30 minutos
    )
    
    return {
        "mensaje": "Token renovado exitosamente",
        "usuario_id": current_user.usuario_id,
        "usuario_email": current_user.usuario_email
    }