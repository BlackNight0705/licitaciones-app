# routes/licitacion_route.py
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from sqlalchemy.orm import selectinload

from backend.app.core.database import get_session
from backend.app.core.security import obtener_usuario_actual
from backend.app.models.licitacion import Licitacion
from backend.app.models.usuario import Usuario
from backend.app.schemas.licitacion_schema import (
    LicitacionCreate,
    LicitacionResponse,
    LicitacionDetailResponse,
    LicitacionUpdate
)
from backend.app.schemas.licitacion_producto_schema import (
    LicitacionProductoCreate,
    LicitacionProductoResponse
)
from backend.app.schemas.historial_transicion_schema import HistorialTransicionResponse
from backend.app.models.historial_transicion import HistorialTransicion
from backend.app.services.licitacion_service import (
    actualizar_licitacion,
    crear_licitacion,
    cambiar_estado_licitacion,
    agregar_producto_licitacion,
    quitar_producto_licitacion,
    subir_documento_licitacion,
    obtener_licitacion_detalle
)
from backend.app.services.upload_service import subir_archivo_general

router = APIRouter(prefix="/licitaciones", tags=["Licitaciones"])

# Ruta para crear una licitación
@router.post("/", response_model=LicitacionResponse, status_code=status.HTTP_201_CREATED)
async def crear_licitacion_route(
    data: LicitacionCreate,
    session: AsyncSession = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return await crear_licitacion(session, data, usuario_actual.usuario_id)

# Listado de licitaciones (Filtrado por usuario actual)
@router.get("/", response_model=List[LicitacionResponse])
async def listar_licitaciones_route(
    skip: int = 0,
    limit: int = 100,
    session: AsyncSession = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    result = await session.execute(
        select(Licitacion)
        .options(selectinload(Licitacion.cliente))
        .where(Licitacion.licitacion_usuario_id == usuario_actual.usuario_id) # <--- ¡Filtro clave añadido!
        .offset(skip)
        .limit(limit)
    )
    return result.scalars().all()

# Ruta para obtener el detalle de una licitación (Pasando el usuario_id)
@router.get("/{licitacion_id}", response_model=LicitacionDetailResponse)
async def obtener_detalle_licitacion_route(
    licitacion_id: int,
    session: AsyncSession = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return await obtener_licitacion_detalle(session, licitacion_id, usuario_actual.usuario_id)

#cambiar estado de una licitación
@router.post("/{licitacion_id}/estado/{nuevo_estado}", response_model=LicitacionResponse)
async def cambiar_estado_route(
    licitacion_id: int,
    nuevo_estado: str,
    session: AsyncSession = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return await cambiar_estado_licitacion(session, licitacion_id, nuevo_estado, usuario_actual.usuario_id)

# Rutas para agregar y quitar productos de una licitación
@router.post("/{licitacion_id}/productos", response_model=LicitacionProductoResponse)
async def agregar_producto_route(
    licitacion_id: int, 
    data: LicitacionProductoCreate, 
    session: AsyncSession = Depends(get_session),
    usuario_actual = Depends(obtener_usuario_actual)
):
    return await agregar_producto_licitacion(session, licitacion_id, data, usuario_actual)

#Quitar producto de una licitación
@router.delete("/{licitacion_id}/productos/{licitacion_producto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def quitar_producto_route(
    licitacion_id: int,
    licitacion_producto_id: int,
    session: AsyncSession = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    await quitar_producto_licitacion(session, licitacion_id, licitacion_producto_id, usuario_actual.usuario_id)
    return None

# Rutas para subir documentos y obtener historial de transiciones
@router.post("/{licitacion_id}/documento")
async def subir_documento_route(
    licitacion_id: int,
    archivo: UploadFile = File(...),
    session: AsyncSession = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    contenido = await archivo.read()
    
    licitacion = await subir_documento_licitacion(
        session=session, 
        licitacion_id=licitacion_id, 
        contenido=contenido, 
        filename=archivo.filename, 
        usuario_id=str(usuario_actual.usuario_id)
    )
    
    return {
        "mensaje": "Documento subido y asociado correctamente",
        "url": licitacion.licitacion_documento_url
    }

#Obtener historial de transiciones de una licitación
@router.get("/{licitacion_id}/historial", response_model=List[HistorialTransicionResponse])
async def obtener_historial_licitacion_route(
    licitacion_id: int,
    session: AsyncSession = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    # Validamos propiedad antes de mostrar el historial
    result_lic = await session.execute(
        select(Licitacion).where(
            Licitacion.licitacion_id == licitacion_id,
            Licitacion.licitacion_usuario_id == usuario_actual.usuario_id
        )
    )
    if not result_lic.scalars().first():
        raise HTTPException(status_code=404, detail="Licitación no encontrada o no tienes permisos")

    result = await session.execute(
        select(HistorialTransicion)
        .where(HistorialTransicion.historial_transicion_licitacion_id == licitacion_id)
        .order_by(HistorialTransicion.historial_transicion_fecha_transicion.asc())
    )
    return result.scalars().all()

@router.put("/{licitacion_id}", response_model=LicitacionResponse)
async def actualizar_licitacion_route(
    licitacion_id: int,
    data: LicitacionUpdate,
    session: AsyncSession = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    return await actualizar_licitacion(session, licitacion_id, data, usuario_actual.usuario_id)