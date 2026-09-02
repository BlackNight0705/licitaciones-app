from backend.app.core.database import async_session
from backend.app.services.licitacion_service import procesar_licitaciones

async def cron_procesar_licitaciones():
    async with async_session() as session:
        await procesar_licitaciones(session) 
