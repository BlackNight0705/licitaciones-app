from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.usuario import Usuario
from backend.app.schemas.usuario_schema import UsuarioCreate

async def create_user(session: AsyncSession, data: UsuarioCreate):
    user = Usuario(email=data.email, name=data.name)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
