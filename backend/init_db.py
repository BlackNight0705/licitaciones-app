import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from app.core.database import Base

# Importación explícita de TODOS tus modelos para que SQLAlchemy los detecte
from app.models.cliente import Cliente
from app.models.historial_transicion import HistorialTransicion
from app.models.licitacion_producto import LicitacionProducto
from app.models.licitacion import Licitacion
from app.models.pago import Pago
from app.models.producto import Producto
from app.models.usuario import Usuario
from app.models.auditoria import AuditLog
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

def init_db():
    print("Conectando a la base de datos de Supabase...")
    engine = create_engine(DATABASE_URL, echo=True)
    
    print("Creando todas las tablas del proyecto...")
    Base.metadata.create_all(bind=engine)
    print("¡Tablas creadas exitosamente!")

if __name__ == "__main__":
    init_db()