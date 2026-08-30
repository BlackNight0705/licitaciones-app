<<<<<<< HEAD
from pydantic_settings import BaseSettings
=======
from pydantic import BaseSettings
>>>>>>> 11d52f023bfa734825f424886b7c12377d32e0ef

class Settings(BaseSettings):
    # Nombre del proyecto
    PROJECT_NAME: str = "Sistema de Licitaciones"

    # Base de datos
    DATABASE_URL: str

    # Seguridad
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 horas

    # Email (Resend / SendGrid)
    EMAIL_API_KEY: str | None = None
    EMAIL_FROM: str | None = None

    # Storage (Supabase Storage)
    STORAGE_URL: str | None = None
    STORAGE_KEY: str | None = None

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instancia global
settings = Settings()
