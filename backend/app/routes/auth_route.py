from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.app.core.database import get_session
from backend.app.models.usuario import Usuario
from backend.app.core.security import verificar_password, crear_access_token

router = APIRouter(tags=["Autenticación"])

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
        max_age=1800       # Tiempo de expiración en segundos (30 min)
    )

    # <--- 3. Devolvemos solo los datos informativos del usuario (el token ya viaja oculto en la cookie)
    return {
        "mensaje": "Login exitoso",
        "usuario_id": usuario.usuario_id,
        "usuario_email": usuario.usuario_email,
        "usuario_rol": usuario.usuario_rol
    }