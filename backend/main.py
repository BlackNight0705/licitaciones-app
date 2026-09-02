print("MAIN.PY CARGADO DESDE:", __file__)
from contextlib import asynccontextmanager
from fastapi import FastAPI

from backend.app.routes.licitacion_route import router as licitacion_router
from backend.app.routes.pago_route import router as pago_router
from backend.app.routes.usuario_route import router as user_router

from backend.app.utils.cron_jobs import cron_procesar_licitaciones

from apscheduler.schedulers.asyncio import AsyncIOScheduler


@asynccontextmanager
async def lifespan(_app):
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        cron_procesar_licitaciones,
        "interval",
        minutes=30
    )
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(lifespan=lifespan)

app.include_router(user_router)
app.include_router(licitacion_router)
app.include_router(pago_router)
