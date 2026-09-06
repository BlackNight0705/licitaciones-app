from fastapi import APIRouter, Depends, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_session
from backend.app.services.auth_service import service_login, service_refresh_token

router = APIRouter(tags=["Autenticación"])

@router.post("/login")
async def login(
    response: Response, 
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session)
):
    resultado = await service_login(session, form_data.username, form_data.password)
    
    usuario = resultado["usuario"]
    access_token = resultado["access_token"]
    refresh_token = resultado["refresh_token"]

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

    return {
        "mensaje": "Login exitoso",
        "usuario_id": usuario.usuario_id,
        "usuario_email": usuario.usuario_email,
        "usuario_rol": usuario.usuario_rol
    }

@router.post("/auth/refresh")
async def refresh_token(
    response: Response, 
    refresh_token: str = Cookie(None), 
    session: AsyncSession = Depends(get_session)
):
    """
    Renueva el access token usando el refresh token almacenado de forma segura.
    """
    resultado = await service_refresh_token(session, refresh_token)
    
    usuario = resultado["usuario"]
    nuevo_access_token = resultado["nuevo_access_token"]
    
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

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key="access_token", samesite="none", secure=True)
    response.delete_cookie(key="refresh_token", samesite="none", secure=True)
    
    return {"mensaje": "Sesión cerrada exitosamente"}