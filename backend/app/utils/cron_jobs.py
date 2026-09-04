from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.app.core.database import SessionLocal
from backend.app.models.licitacion import Licitacion
from backend.app.models.historial_transicion import HistorialTransicion
from backend.app.services.email_service import enviar_recordatorio, enviar_correo_vencida

async def cron_procesar_licitaciones():
    async with SessionLocal() as session:
        result = await session.execute(
            select(Licitacion)
            .options(selectinload(Licitacion.cliente))
            .where(Licitacion.licitacion_estado == "activa")
        )
        licitaciones = result.scalars().all()
        
        ahora = datetime.utcnow()
        for licitacion in licitaciones:
            if licitacion.licitacion_fecha_limite:
                tiempo_restante = licitacion.licitacion_fecha_limite - ahora
                
                # 1. Si ya pasó la fecha límite -> Marcar como perdida y notificar
                if tiempo_restante.total_seconds() <= 0:
                    estado_anterior = licitacion.licitacion_estado
                    licitacion.licitacion_estado = "perdida"
                    
                    historial = HistorialTransicion(
                        historial_transicion_licitacion_id=licitacion.licitacion_id,
                        historial_transicion_estado_anterior=estado_anterior,
                        historial_transicion_estado_nuevo="perdida",
                        historial_transicion_usuario_id=1,
                        historial_transicion_fecha_transicion=ahora
                    )
                    session.add(historial)
                    session.add(licitacion)
                    
                    cliente_email = getattr(licitacion.cliente, "cliente_email", None) if licitacion.cliente else None
                    if cliente_email:
                        await enviar_correo_vencida(
                            cliente_email=cliente_email,
                            titulo=licitacion.licitacion_titulo
                        )
                
                # 2. Si faltan menos de 48 horas -> Enviar recordatorio (puedes agregar un flag de control si deseas evitar duplicados)
                elif timedelta(hours=0) < tiempo_restante <= timedelta(hours=48):
                    cliente_email = getattr(licitacion.cliente, "cliente_email", None) if licitacion.cliente else None
                    if cliente_email:
                        await enviar_recordatorio(
                            cliente_email=cliente_email,
                            titulo=licitacion.licitacion_titulo,
                            fecha_limite=str(licitacion.licitacion_fecha_limite)
                        )
        
        await session.commit()