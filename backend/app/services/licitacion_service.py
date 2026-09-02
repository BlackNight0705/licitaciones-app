#Este archivo define los servicios relacionados con las licitaciones en la aplicación FastAPI. Incluye funciones para crear licitaciones, cambiar su estado, aprobarlas y subir documentos asociados.
import re
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime, timedelta

from supabase import create_client, Client
from backend.app.core.config import settings
from backend.app.models.licitacion import Licitacion
from backend.app.models.historial_transicion import HistorialTransicion

# Inicializar cliente de Supabase usando la URL limpia y la llave service_role
supabase: Client = create_client(settings.STORAGE_URL, settings.STORAGE_KEY)

def limpiar_filename(filename: str) -> str:
    filename = filename.strip()
    filename = filename.replace(" ", "_")
    filename = re.sub(r"[^A-Za-z0-9._-]", "", filename)
    return filename

# Crear licitación (Directa, sin dependencias de convocatorias)
async def crear_licitacion(session: AsyncSession, data):
    licitacion = Licitacion(**data.model_dump())
    session.add(licitacion)
    await session.commit()
    await session.refresh(licitacion)
    return licitacion

# Cambiar estado de licitación
async def cambiar_estado(session: AsyncSession, licitacion_id: int, nuevo_estado: str, usuario_id: int):
    licitacion = await session.get(Licitacion, licitacion_id)
    if not licitacion:
        raise ValueError("Licitación no encontrada")
        
    anterior = licitacion.licitacion_estado

    transiciones_validas = {
        "borrador": ["evaluacion"],
        "evaluacion": ["activa", "perdida"],
        "activa": ["finalizada", "perdida"],
        "finalizada": ["por_cobrar"],
        "por_cobrar": ["cobrada"],
    }

    if nuevo_estado not in transiciones_validas.get(anterior, []):
        raise ValueError(f"No se puede pasar de {anterior} a {nuevo_estado}")

    licitacion.licitacion_estado = nuevo_estado

    historial = HistorialTransicion(
        historial_transicion_licitacion_id=licitacion_id,
        historial_transicion_estado_anterior=anterior,
        historial_transicion_estado_nuevo=nuevo_estado,
        historial_transicion_usuario_id=usuario_id,
        historial_transicion_fecha_transicion=datetime.utcnow()
    )

    session.add(historial)
    await session.commit()
    await session.refresh(licitacion)
    return licitacion

# Aprobar licitación
async def aprobar_licitacion(session: AsyncSession, licitacion_id: int, usuario_admin_id: int):
    licitacion = await session.get(Licitacion, licitacion_id)
    if not licitacion:
        raise ValueError("Licitación no encontrada")
        
    licitacion.licitacion_aprobada_por_admin = True
    anterior = licitacion.licitacion_estado
    licitacion.licitacion_estado = "activa"

    historial = HistorialTransicion(
        historial_transicion_licitacion_id=licitacion_id,
        historial_transicion_estado_anterior=anterior,
        historial_transicion_estado_nuevo="activa",
        historial_transicion_usuario_id=usuario_admin_id,
        historial_transicion_fecha_transicion=datetime.utcnow()
    )

    session.add(historial)
    await session.commit()
    await session.refresh(licitacion)
    return licitacion

# Service para subir documento a licitación con la estructura Licitaciones/{user_id}/archivo
async def subir_documento_licitacion(session: AsyncSession, licitacion_id: int, contenido: bytes, filename: str, user_id: str):
    licitacion = await session.get(Licitacion, licitacion_id)
    if not licitacion:
        raise ValueError("Licitación no encontrada")

    filename_limpio = limpiar_filename(filename)
    bucket = "licitaciones_archivos"
    
    # Ruta estricta validada por las políticas RLS de Supabase
    ruta_en_bucket = f"Licitaciones/{user_id}/{filename_limpio}"

    try:
        supabase.storage.from_(bucket).upload(
            path=ruta_en_bucket,
            file=contenido,
            file_options={"content-type": "application/octet-stream", "upsert": "true"}
        )
    except Exception as e:
        print(f"Error subiendo archivo a Supabase: {e}")
        raise Exception("Error subiendo archivo al storage")

    # Obtener la URL pública del archivo
    public_url_response = supabase.storage.from_(bucket).get_public_url(ruta_en_bucket)
    documento_url = public_url_response if isinstance(public_url_response, str) else public_url_response.get("publicUrl")

    # Guardar la URL en el campo correspondiente del modelo
    licitacion.licitacion_documento_url = documento_url

    await session.commit()
    await session.refresh(licitacion)
    return licitacion

# Service para procesar licitaciones activas y enviar recordatorios o marcar como perdidas
async def procesar_licitaciones(session: AsyncSession):
    ahora = datetime.utcnow()

    # Buscar licitaciones activas
    result = await session.execute(
        select(Licitacion).where(Licitacion.licitacion_estado == "activa")
    )
    licitaciones = result.scalars().all()

    for lic in licitaciones:
        # Si faltan 48 horas → enviar recordatorio
        if lic.licitacion_fecha_limite - ahora <= timedelta(hours=48):
            # Aquí llamas tu servicio de correo
            pass

        # Si ya venció → marcar como perdida
        if ahora > lic.licitacion_fecha_limite:
            anterior = lic.licitacion_estado
            lic.licitacion_estado = "perdida"

            historial = HistorialTransicion(
                historial_transicion_licitacion_id=lic.licitacion_id,
                historial_transicion_estado_anterior=anterior,
                historial_transicion_estado_nuevo="perdida",
                historial_transicion_usuario_id=1,  # sistema
                historial_transicion_fecha_transicion=ahora
            )

            session.add(historial)

    await session.commit()