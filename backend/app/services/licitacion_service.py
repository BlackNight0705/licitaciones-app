# Este archivo contiene funciones de servicio para manejar operaciones relacionadas con licitaciones, incluyendo creación, cambio de estado, gestión de productos y documentos.
from psycopg2 import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from datetime import datetime
from backend.app.core.config import settings

from backend.app.models.licitacion import Licitacion
from backend.app.models.licitacion_producto import LicitacionProducto
from backend.app.models.historial_transicion import HistorialTransicion
from backend.app.models.producto import Producto
from backend.app.schemas.licitacion_schema import LicitacionCreate, LicitacionUpdate
from backend.app.schemas.licitacion_producto_schema import LicitacionProductoCreate
from backend.app.services.upload_service import subir_archivo_general
# Importamos todos los servicios de correo necesarios
from backend.app.services.email_service import (
    enviar_correo_activacion,
    enviar_correo_vencida
)

TRANSICIONES_VALIDAS = {
    "borrador": ["activa", "perdida"],
    "activa": ["ganada", "finalizada", "perdida"],
    "ganada": ["por_cobrar", "perdida"],
    "finalizada": ["por_cobrar", "perdida"],
    "por_cobrar": ["cobrada", "perdida"],
    "cobrada": [],
    "perdida": []
}

async def _disparar_correo_seguro(licitacion: Licitacion, estado_nuevo: str):
    """Función auxiliar segura para enviar correos según el estado al que transicione la licitación."""
    try:
        cliente_email = getattr(licitacion.cliente, "cliente_email", None) if licitacion.cliente else None
        if not cliente_email:
            return

        if estado_nuevo == "activa":
            fecha_limite_str = str(licitacion.licitacion_fecha_limite) if licitacion.licitacion_fecha_limite else "Sin definir"
            documento_url = licitacion.licitacion_documento_url or ""
            await enviar_correo_activacion(
                cliente_email=cliente_email,
                titulo=licitacion.licitacion_titulo,
                fecha_limite=fecha_limite_str,
                documento_url=documento_url
            )
        elif estado_nuevo == "perdida":
            await enviar_correo_vencida(
                cliente_email=cliente_email,
                titulo=licitacion.licitacion_titulo
            )
        # Puedes agregar más 'elif' aquí si necesitas notificar para 'finalizada', 'por_cobrar', etc.
            
    except Exception as e:
        print(f"Error al intentar enviar el correo de notificación: {e}")

# Funcion para crear una licitacion
async def crear_licitacion(session: AsyncSession, data: LicitacionCreate, usuario_id: int) -> Licitacion:
    try:
        licitacion = Licitacion(
            licitacion_titulo=data.licitacion_titulo,
            licitacion_descripcion=data.licitacion_descripcion,
            licitacion_presupuesto_maximo=data.licitacion_presupuesto_maximo,
            licitacion_fecha_limite=data.licitacion_fecha_limite,
            licitacion_cliente_id=data.licitacion_cliente_id,
            licitacion_usuario_id=usuario_id,
            licitacion_estado="borrador",
            entidad_creador_id=usuario_id,
            entidad_modificador_id=usuario_id
        )
        session.add(licitacion)
        await session.commit()
        await session.refresh(licitacion)
        return licitacion
    except Exception as e:
        await session.rollback()
        raise HTTPException(status_code=400, detail=f"Error en la base de datos: {str(e)}")

# Funcion para actualizar la licitacion y manejar la transición controlada
async def actualizar_licitacion(session: AsyncSession, licitacion_id: int, data: LicitacionUpdate, usuario_id: int) -> Licitacion:
    result = await session.execute(
        select(Licitacion)
        .options(selectinload(Licitacion.productos), selectinload(Licitacion.cliente))
        .where(Licitacion.licitacion_id == licitacion_id)
    )
    licitacion = result.scalars().first()
    if not licitacion:
        raise HTTPException(status_code=404, detail="Licitación no encontrada")

    estado_anterior = licitacion.licitacion_estado
    nuevo_estado = data.licitacion_estado

    if nuevo_estado and nuevo_estado != estado_anterior:
        if nuevo_estado not in TRANSICIONES_VALIDAS.get(estado_anterior, []):
            raise HTTPException(
                status_code=400,
                detail=f"Transición no permitida de '{estado_anterior}' a '{nuevo_estado}'."
            )

        if estado_anterior == "borrador" and nuevo_estado == "activa":
            if not licitacion.licitacion_documento_url:
                raise HTTPException(
                    status_code=400,
                    detail="No se puede activar la licitación sin un documento de propuesta adjunto."
                )
            if not licitacion.productos or len(licitacion.productos) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="No se puede activar la licitación porque debe tener al menos un producto agregado."
                )

        licitacion.licitacion_estado = nuevo_estado

        historial = HistorialTransicion(
            historial_transicion_licitacion_id=licitacion_id,
            historial_transicion_estado_anterior=estado_anterior,
            historial_transicion_estado_nuevo=nuevo_estado,
            historial_transicion_usuario_id=usuario_id,
            historial_transicion_fecha_transicion=datetime.utcnow()
        )
        session.add(historial)

    update_data = data.model_dump(exclude_unset=True)
    update_data.pop("licitacion_estado", None)

    for key, value in update_data.items():
        setattr(licitacion, key, value)

    licitacion.entidad_modificador_id = usuario_id

    await session.commit()
    await session.refresh(licitacion)

    # Disparamos el correo de forma segura si el estado cambió realmente
    if nuevo_estado and nuevo_estado != estado_anterior:
        await _disparar_correo_seguro(licitacion, nuevo_estado)

    return licitacion
    
# Funcion para cambiar el estado de la licitacion de forma directa
async def cambiar_estado_licitacion(session: AsyncSession, licitacion_id: int, nuevo_estado: str, usuario_id: int) -> Licitacion:
    result = await session.execute(
        select(Licitacion)
        .options(selectinload(Licitacion.cliente))
        .where(Licitacion.licitacion_id == licitacion_id)
    )
    licitacion = result.scalars().first()
    if not licitacion:
        raise HTTPException(status_code=404, detail="Licitación no encontrada")

    estado_actual = licitacion.licitacion_estado

    if nuevo_estado not in TRANSICIONES_VALIDAS.get(estado_actual, []):
        raise HTTPException(
            status_code=400,
            detail=f"Transición no permitida de '{estado_actual}' a '{nuevo_estado}'."
        )

    if estado_actual == "borrador" and nuevo_estado == "activa":
        if not licitacion.licitacion_documento_url:
            raise HTTPException(
                status_code=400,
                detail="No se puede activar la licitación sin un documento de propuesta adjunto."
            )

    licitacion.licitacion_estado = nuevo_estado

    historial = HistorialTransicion(
        historial_transicion_licitacion_id=licitacion_id,
        historial_transicion_estado_anterior=estado_actual,
        historial_transicion_estado_nuevo=nuevo_estado,
        historial_transicion_usuario_id=usuario_id,
        historial_transicion_fecha_transicion=datetime.utcnow()
    )

    session.add(historial)
    await session.commit()
    await session.refresh(licitacion)

    # Disparamos el correo de forma segura al cambiar de estado aquí también
    await _disparar_correo_seguro(licitacion, nuevo_estado)

    return licitacion

# Funcion para agregar un producto a la licitacion
async def agregar_producto_licitacion(session: AsyncSession, licitacion_id: int, data, usuario_current) -> LicitacionProducto:
    licitacion = await session.get(Licitacion, licitacion_id)
    if not licitacion:
        raise HTTPException(status_code=404, detail="Licitación no encontrada")

    stmt = select(Producto).where(Producto.producto_nombre == data.nombre)
    result = await session.execute(stmt)
    producto = result.scalars().first()

    if not producto:
        producto = Producto(
            producto_nombre=data.nombre,
            producto_precio_unitario=data.precio_unitario,
            entidad_creador_id=usuario_current.usuario_id
        )
        session.add(producto)
        await session.flush()

    licitacion_producto = LicitacionProducto(
        licitacion_producto_licitacion_id=licitacion_id,
        licitacion_producto_producto_id=producto.producto_id,
        licitacion_producto_cantidad=data.cantidad,
        licitacion_producto_precio_unitario=data.precio_unitario,
        entidad_creador_id=usuario_current.usuario_id 
    )
    
    session.add(licitacion_producto)
    await session.commit()
    await session.refresh(licitacion_producto)
    return licitacion_producto

# Funcion para quitar un producto de la licitacion
async def quitar_producto_licitacion(session: AsyncSession, licitacion_id: int, licitacion_producto_id: int):
    producto = await session.get(LicitacionProducto, licitacion_producto_id)
    if not producto or producto.licitacion_producto_licitacion_id != licitacion_id:
        raise HTTPException(status_code=404, detail="Producto no encontrado en esta licitación")

    await session.delete(producto)
    await session.commit()

# Funcion para subir documento a la licitacion
async def subir_documento_licitacion(session: AsyncSession, licitacion_id: int, contenido: bytes, filename: str, usuario_id: str) -> Licitacion:
    licitacion = await session.get(Licitacion, licitacion_id)
    if not licitacion:
        raise HTTPException(status_code=404, detail="Licitación no encontrada")

    url_real = await subir_archivo_general(contenido, filename, usuario_id)
    licitacion.licitacion_documento_url = url_real

    await session.commit()
    await session.refresh(licitacion)
    return licitacion

# Funcion para obtener el detalle de la licitacion, incluyendo cliente, productos e historial
async def obtener_licitacion_detalle(session: AsyncSession, licitacion_id: int) -> Licitacion:
    result = await session.execute(
        select(Licitacion)
        .options(
            selectinload(Licitacion.cliente),
            selectinload(Licitacion.productos),
            selectinload(Licitacion.historial)
        )
        .where(Licitacion.licitacion_id == licitacion_id)
    )
    licitacion = result.scalars().first()
    if not licitacion:
        raise HTTPException(status_code=404, detail="Licitación no encontrada")
    return licitacion