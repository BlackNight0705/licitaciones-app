# Sistema de Gestión de Licitaciones

Aplicación web full-stack diseñada para la administración integral de procesos de licitaciones comerciales, control de estados del ciclo de vida, gestión de propuestas con almacenamiento en la nube, procesamiento de reglas de negocio y envío de notificaciones transaccionales automáticas por correo electrónico.

## Enlace al Despliegue

- **Aplicación en Línea:** https://licitaciones-web-6ej9.onrender.com/login

## Arquitectura y Tecnologías

- **Frontend:** 
  - React (JavaScript/JSX)
  - React Router para enrutamiento dinámico y rutas protegidas
  - Tailwind CSS para el sistema de estilos y componentes
  - Lucide React para iconografía de interfaz
- **Backend / API:** 
  - FastAPI (Python) con Uvicorn como servidor ASGI
  - Autenticación basada en PyJWT y contraseñas cifradas con Bcrypt / Passlib
  - Control de roles de usuario
- **Base de Datos y Almacenamiento:** 
  - PostgreSQL para persistencia relacional conectada mediante SQLAlchemy y Asyncpg / Psycopg2
  - Control de migraciones de base de datos ejecutado con Alembic
  - Supabase y librerías de soporte (Postgrest, Storage3, Realtime) para la gestión y almacenamiento de archivos de propuestas
- **Servicios Externos:** 
  - Resend para el envío transaccional de correos electrónicos con soporte nativo para archivos adjuntos[cite: 1]
  - APScheduler para la automatización de tareas programadas (Background Jobs / Cron) orientadas al control de vencimientos y envío de recordatorios a 48 horas[cite: 1]

## Estructura del Proyecto

```text
licitaciones-app/
│
├── frontend/             # Código fuente de la interfaz de usuario (React)
│   ├── src/
│   │   ├── api/          # Módulos de comunicación con el backend
│   │   ├── components/   # Componentes reutilizables (Sidebar, Navbar, Modales, etc.)
│   │   ├── context/      # Contexto de autenticación (AuthContext)
│   │   └── pages/        # Vistas principales (LoginPage, DashboardPage, LicitacionDetailPage)
│   └── package.json
│
└── backend/              # Lógica del servidor, modelos y controladores de API (Python/FastAPI)
    ├── app/
    │   ├── core/         # Configuración general y seguridad
    │   ├── models/       # Esquemas de base de datos SQLAlchemy
    │   ├── routes/       # Endpoints de Clientes, Licitaciones, Productos y Pagos[cite: 1]
    │   ├── schemas/      # Modelos Pydantic para validación de datos
    │   ├── services/     # Integración de correo, almacenamiento y programador de tareas
    │   └── utils/        # Utilidades y funciones auxiliares
    ├── init_db.py        # Script de inicialización de la base de datos
    ├── main.py           # Punto de entrada de la aplicación FastAPI
    └── requirements.txt  # Dependencias del proyecto
```

## Reglas de Negocio Implementadas
* Control de Acceso: Autenticación obligatoria con control de roles (administrador y usuario)[cite: 1].
* Ciclo de Estado de Licitaciones: Flujo controlado entre los estados borrador, activa, finalizada, por_cobrar, cobrada y perdida[cite: 1]. Transiciones no válidas son rechazadas por la API[cite: 1].
* Validación de Documentos: Una licitación en estado borrador solo puede transicionar a activa si cuenta estrictamente con un documento de propuesta adjunto[cite: 1].
* Presupuesto Máximo: La suma de los precios por cantidad de los productos asociados no puede superar el presupuesto máximo configurado en la licitación[cite: 1].
* Automatización Temporal: Verificación automática periódica mediante APScheduler para transicionar a estado perdida aquellas licitaciones activas cuya fecha límite haya expirado, así como el envío de correos de recordatorio dentro del plazo de 48 horas previas al cierre[cite: 1].
* Auditoría: Registro detallado en el historial de transiciones de cada cambio de estado, incluyendo usuario responsable, marca de tiempo y estado anterior/nuevo[cite: 1].

## Requisitos Previos
Antes de ejecutar el proyecto de manera local, asegúrese de contar con:
* Node.js (versión 18 o superior)
* Python (versión 3.10 o superior)
* Instancia de PostgreSQL (local o en la nube mediante Supabase)[cite: 1]

## Instrucciones de Instalación y Ejecución Local

### 1. Clonar el Repositorio
```bash
git clone [https://github.com/BlackNight0705/licitaciones-app.git](https://github.com/BlackNight0705/licitaciones-app.git)
cd licitaciones-app
```

### 2. Configuración de Variables de Entorno
Crear un archivo `.env` en la carpeta del backend y otro en la del frontend según los parámetros requeridos:

**Backend (.env):**
```env
DATABASE_URL=url a base de datos
JWT_SECRET=tu_clave_secreta_jwt
EMAIL_API_KEY=tu_api_key_resend
EMAIL_FROM=Correo de resend a utilizar
STORAGE_URL=tu_url_supabase
STORAGE_KEY=tu_clave_supabase
URL_Online=URL de servicio de servidor a usar o localhost para el backend
```

**Frontend (.env):**
```env
VITE_API_URL=http://localhost:8000/api <-cambiar por ruta web si van a desplegar
```

**4. Ejecución en el Backend:**
```pwd
cd licitaciones_app
python -m venv venv
# En Windows: venv\Scripts\activate | En Mac/Linux: source venv/bin/activate
pip install -r backend/requirements.txt
alembic upgrade head
uvicorn main:app --reload <-online uvicorn backend.main:app --reload <- local
```

**5. Ejecución de Frontend:**
```pwd
cd ../frontend
npm install 
npm run dev
```
*Nota: tener Node.js ya instalado para ejecutar el Front*


#Usuario de Prueba(Admin)
*Nota: notese que el admin tiene funciones, distintas a las de un user normal, puede crear un usuario y un cliente con correo valido con servivio
resend y este podra servir de prueba para el correo, si no, puede probar laas otras funcionalidades*

```
Admin:admin_prb@correonoutil.com
Contraseña: Admonpsw___001
```

#Evidencias
Se adjuntaron algunas evidencias de uso dentro del sitio y algunos de sus servivios
```![Texto alternativo de la imagen](./img/banner.png)```
