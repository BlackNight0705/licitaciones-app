from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.routes.licitacion_route import router as licitacion_router
from backend.app.routes.pago_route import router as pago_router
from backend.app.routes.usuario_route import router as user_router
from backend.app.routes.cliente_route import router as cliente_route
from backend.app.routes.auth_route import router as auth_router

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


app = FastAPI(
    title="Sistema de Licitaciones API",
    lifespan=lifespan
)

# Configuración de CORS para permitir conexiones desde el frontend (Vite)
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de routers
app.include_router(user_router)
app.include_router(licitacion_router)
app.include_router(pago_router)
app.include_router(cliente_route)
app.include_router(auth_router)