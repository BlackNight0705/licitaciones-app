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
from backend.app.models.auditoria import AuditLog
from backend.app.models.historial_transicion import HistorialTransicion
from backend.app.services.licitacion_service import (
    actualizar_licitacion,
    crear_licitacion,
    cambiar_estado_licitacion,
    agregar_producto_licitacion,
    eliminar_licitacion,
    quitar_producto_licitacion,
    subir_documento_licitacion,
    obtener_licitacion_detalle
)
from backend.app.services.upload_service import subir_archivo_general

router = APIRouter(prefix="/licitaciones", tags=["Licitaciones"])

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

# Ruta para crear una licitación
@router.post("/", response_model=LicitacionResponse, status_code=status.HTTP_201_CREATED)
async def crear_licitacion_route(
    data: LicitacionCreate,
    session: AsyncSession = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    licitacion = await crear_licitacion(session, data, usuario_actual.usuario_id)
    
    await registrar_accion(
        session=session,
        usuario_id=usuario_actual.usuario_id,
        accion="CREAR",
        modulo="Licitaciones",
        detalles=f"El usuario creó la licitación con ID {licitacion.licitacion_id}."
    )
    
    return licitacion

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
        .where(Licitacion.licitacion_usuario_id == usuario_actual.usuario_id)
        .offset(skip)
        .limit(limit)
    )
    licitaciones = result.scalars().all()
    
    await registrar_accion(
        session=session,
        usuario_id=usuario_actual.usuario_id,
        accion="CONSULTA",
        modulo="Licitaciones",
        detalles="El usuario consultó el listado de sus licitaciones."
    )
    
    return licitaciones

# Ruta para obtener el detalle de una licitación (Pasando el usuario_id)
@router.get("/{licitacion_id}", response_model=LicitacionDetailResponse)
async def obtener_detalle_licitacion_route(
    licitacion_id: int,
    session: AsyncSession = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    licitacion = await obtener_licitacion_detalle(session, licitacion_id, usuario_actual.usuario_id)
    
    await registrar_accion(
        session=session,
        usuario_id=usuario_actual.usuario_id,
        accion="CONSULTA",
        modulo="Licitaciones",
        detalles=f"El usuario consultó el detalle de la licitación ID {licitacion_id}."
    )
    
    return licitacion

#cambiar estado de una licitación
@router.post("/{licitacion_id}/estado/{nuevo_estado}", response_model=LicitacionResponse)
async def cambiar_estado_route(
    licitacion_id: int,
    nuevo_estado: str,
    session: AsyncSession = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    licitacion = await cambiar_estado_licitacion(session, licitacion_id, nuevo_estado, usuario_actual.usuario_id)
    
    await registrar_accion(
        session=session,
        usuario_id=usuario_actual.usuario_id,
        accion="ACTUALIZAR",
        modulo="Licitaciones",
        detalles=f"El usuario cambió el estado de la licitación ID {licitacion_id} a {nuevo_estado}."
    )
    
    return licitacion

# Rutas para agregar y quitar productos de una licitación
@router.post("/{licitacion_id}/productos", response_model=LicitacionProductoResponse)
async def agregar_producto_route(
    licitacion_id: int, 
    data: LicitacionProductoCreate, 
    session: AsyncSession = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    producto_licitacion = await agregar_producto_licitacion(session, licitacion_id, data, usuario_actual)
    
    await registrar_accion(
        session=session,
        usuario_id=usuario_actual.usuario_id,
        accion="CREAR",
        modulo="Licitaciones",
        detalles=f"El usuario agregó un producto a la licitación ID {licitacion_id}."
    )
    
    return producto_licitacion

#Quitar producto de una licitación
@router.delete("/{licitacion_id}/productos/{licitacion_producto_id}", status_code=status.HTTP_204_NO_CONTENT)
async def quitar_producto_route(
    licitacion_id: int,
    licitacion_producto_id: int,
    session: AsyncSession = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    await quitar_producto_licitacion(session, licitacion_id, licitacion_producto_id, usuario_actual.usuario_id)
    
    await registrar_accion(
        session=session,
        usuario_id=usuario_actual.usuario_id,
        accion="ELIMINAR",
        modulo="Licitaciones",
        detalles=f"El usuario eliminó el producto ID {licitacion_producto_id} de la licitación ID {licitacion_id}."
    )
    
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
    
    await registrar_accion(
        session=session,
        usuario_id=usuario_actual.usuario_id,
        accion="ACTUALIZAR",
        modulo="Licitaciones",
        detalles=f"El usuario subió un documento a la licitación ID {licitacion_id}."
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
    historial = result.scalars().all()
    
    await registrar_accion(
        session=session,
        usuario_id=usuario_actual.usuario_id,
        accion="CONSULTA",
        modulo="Licitaciones",
        detalles=f"El usuario consultó el historial de transiciones de la licitación ID {licitacion_id}."
    )
    
    return historial

@router.put("/{licitacion_id}", response_model=LicitacionResponse)
async def actualizar_licitacion_route(
    licitacion_id: int,
    data: LicitacionUpdate,
    session: AsyncSession = Depends(get_session),
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    licitacion = await actualizar_licitacion(session, licitacion_id, data, usuario_actual.usuario_id)
    
    await registrar_accion(
        session=session,
        usuario_id=usuario_actual.usuario_id,
        accion="ACTUALIZAR",
        modulo="Licitaciones",
        detalles=f"El usuario actualizó la información de la licitación ID {licitacion_id}."
    )
    
    return licitacion

#Eliminar licitación (con validación de usuario)
@router.delete("/{licitacion_id}", status_code=status.HTTP_200_OK)
async def eliminar_licitacion_route(
    licitacion_id: int, 
    session: AsyncSession = Depends(get_session), 
    usuario_actual: Usuario = Depends(obtener_usuario_actual)
):
    result = await session.execute(
        select(Licitacion).where(
            Licitacion.licitacion_id == licitacion_id,
            Licitacion.licitacion_usuario_id == usuario_actual.usuario_id
        )
    )
    licitacion = result.scalars().first()
    
    if not licitacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="La licitación no existe o no tienes permisos para eliminarla."
        )
    
    await session.delete(licitacion)
    await session.commit()
    
    await registrar_accion(
        session=session,
        usuario_id=usuario_actual.usuario_id,
        accion="ELIMINAR",
        modulo="Licitaciones",
        detalles=f"El usuario eliminó la licitación ID {licitacion_id}."
    )
    
    return {"message": "Licitación eliminada con éxito"}