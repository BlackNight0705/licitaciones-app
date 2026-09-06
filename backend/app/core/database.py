# core/database.py
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base
from backend.app.core.config import settings
from typing import AsyncGenerator

# Convertimos la URL para asegurar el uso de asyncpg
DATABASE_URL = settings.DATABASE_URL.replace(
    "postgresql://",
    "postgresql+asyncpg://"
)

# Motor async usando la URL corregida
engine = create_async_engine(DATABASE_URL, echo=True)

# Base declarativa para los modelos
Base = declarative_base()
Base.metadata.schema = "public"

# Fábrica de sesiones principal
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Dependencia para FastAPI
async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        yield session