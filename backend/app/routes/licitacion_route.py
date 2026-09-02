#Este archivo define las rutas relacionadas con las licitaciones en la aplicación FastAPI. Incluye rutas para crear licitaciones, subir documentos, cambiar el estado y aprobar licitaciones.
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.database import get_session

from backend.app.schemas.licitacion_schema import LicitacionCreate, LicitacionResponse
from backend.app.services.licitacion_service import (
    crear_licitacion,
    cambiar_estado,
    aprobar_licitacion
)
# Importamos tu servicio de subida a Supabase
from backend.app.services.upload_service import subir_archivo_general

router = APIRouter(prefix="/licitaciones", tags=["Licitaciones"])

# Crear licitación
@router.post("/", response_model=LicitacionResponse)
async def crear_licitacion_route(
    data: LicitacionCreate,
    session: AsyncSession = Depends(get_session)
):
    return await crear_licitacion(session, data)

# Subir documento a licitación (Integrado con Supabase Storage)
@router.post("/{licitacion_id}/documento")
async def subir_documento_route(
    licitacion_id: int,
    archivo: UploadFile = File(...),
    usuario_id: str = "872a6662-6afb-4fee-bd01-b3fba3e0f4d0", # Idealmente esto viene de tu auth/token actual
    session: AsyncSession = Depends(get_session)
):
    try:
        contenido = await archivo.read()
        
        # 1. Sube el archivo a Supabase bajo la ruta Licitaciones/{usuario_id}/archivo.pdf
        url_publica = await subir_archivo_general(contenido, archivo.filename, usuario_id)
        
        # 2. Aquí puedes opcionalmente guardar el link (`url_publica`) en tu base de datos 
        # asociado a la licitación y al usuario usando la sesión (`session`).
        
        return {
            "mensaje": "Archivo subido exitosamente a Supabase",
            "url": url_publica,
            "licitacion_id": licitacion_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Cambiar estado de licitación
@router.post("/{licitacion_id}/estado/{nuevo_estado}")
async def cambiar_estado_route(
    licitacion_id: int,
    nuevo_estado: str,
    usuario_id: int,
    session: AsyncSession = Depends(get_session)
):
    return await cambiar_estado(session, licitacion_id, nuevo_estado, usuario_id)

# Aprobar licitacion
@router.post("/{licitacion_id}/aprobar")
async def aprobar_licitacion_route(
    licitacion_id: int,
    usuario_admin_id: int,
    session: AsyncSession = Depends(get_session)
):
    return await aprobar_licitacion(session, licitacion_id, usuario_admin_id)