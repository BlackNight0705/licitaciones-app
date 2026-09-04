from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_session
from backend.app.models.usuario import Usuario
from backend.app.core.config import settings

# Modificamos o creamos una clase personalizada para leer el token desde la Cookie HttpOnly
class OAuth2PasswordBearerWithCookie(OAuth2PasswordBearer):
    def __init__(self, tokenUrl: str):
        super().__init__(tokenUrl=tokenUrl, auto_error=False)

    async def __call__(self, request: Request) -> Optional[str]:
        # Primero intentamos obtener el token desde la cookie HttpOnly
        token = request.cookies.get("access_token")
        if not token:
            # Si no está en la cookie, recurrimos al comportamiento por defecto (Header Authorization)
            token = await super().__call__(request)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No se encontraron credenciales de autenticación",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return token

oauth2_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/login")

def verificar_password(password_plana: str, password_hashed: str) -> bool:
    return bcrypt.checkpw(
        password_plana.encode('utf-8'), 
        password_hashed.encode('utf-8')
    )

def obtener_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')

def crear_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

async def obtener_usuario_actual(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_session)
) -> Usuario:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        usuario_id: int = payload.get("sub")
        if usuario_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    usuario = await session.get(Usuario, int(usuario_id))
    if usuario is None:
        raise credentials_exception
    return usuario

async def verificar_rol_admin(usuario_actual: Usuario = Depends(obtener_usuario_actual)) -> Usuario:
    if usuario_actual.usuario_rol != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acceso denegado. Se requieren privilegios de administrador."
        )
    return usuario_actual