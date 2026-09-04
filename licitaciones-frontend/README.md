# Portal de Licitaciones — Frontend

Frontend en React + Vite + Tailwind CSS para el sistema de gestión de licitaciones,
conectado a un backend FastAPI con autenticación OAuth2 / JWT.

## Stack

- **React 18** + **Vite** (arranque rápido, sin overhead de SSR ya que es un panel interno)
- **React Router v6** para el enrutado (rutas públicas/privadas)
- **Tailwind CSS** para estilos, con paleta de marca (blancos / lilas / morado profundo)
- **Axios** con interceptores para inyectar el JWT y manejar sesiones expiradas (401)
- **Lucide React** para iconografía

## Estructura de carpetas

```
src/
├── api/                        # Toda la comunicación con el backend
│   ├── axiosClient.js          # Instancia de Axios + interceptores JWT
│   ├── auth.js                 # POST /login (OAuth2PasswordRequestForm)
│   └── licitaciones.js         # Licitaciones, productos, documentos, historial
├── context/
│   └── AuthContext.jsx         # Estado global de sesión (token, login, logout)
├── routes/
│   └── PrivateRoute.jsx        # Guard de rutas autenticadas
├── components/
│   ├── layout/                 # Sidebar, Navbar, DashboardLayout
│   ├── ui/                     # Badge, Modal (componentes genéricos)
│   ├── licitaciones/           # LicitacionForm, EstadoSelector
│   ├── productos/               # ProductoForm, ProductoList
│   ├── documentos/              # UploadDocumento (drag & drop)
│   └── historial/                # HistorialList
├── pages/
│   ├── LoginPage.jsx
│   ├── DashboardPage.jsx        # Listado de licitaciones
│   └── LicitacionDetailPage.jsx # Detalle + productos + documentos + historial
├── App.jsx
├── main.jsx
└── index.css
```

## Puesta en marcha

```bash
npm install
cp .env.example .env       # ajusta VITE_API_BASE_URL si tu backend no está en :8000
npm run dev
```

La app queda disponible en `http://localhost:5173` y espera el backend FastAPI en
`http://localhost:8000` (configurable vía `VITE_API_BASE_URL`).

## Cómo funciona la autenticación

1. `LoginPage` llama a `login()` del `AuthContext`, que a su vez llama a `POST /login`
   enviando `username`/`password` como `application/x-www-form-urlencoded`
   (formato que espera `OAuth2PasswordRequestForm` en FastAPI).
2. El `access_token` recibido se guarda en `localStorage` (clave `licitaciones_token`).
3. `axiosClient` intercepta **cada** petición saliente y añade automáticamente
   la cabecera `Authorization: Bearer <token>`.
4. Si el backend responde `401` (token vencido o inválido), el interceptor de
   respuesta limpia la sesión y redirige a `/login` automáticamente.
5. `PrivateRoute` protege todas las rutas del panel: sin token válido, no se
   puede acceder al dashboard ni al detalle de licitaciones.

## Endpoints consumidos

| Acción                          | Método | Endpoint                                             |
|----------------------------------|--------|-------------------------------------------------------|
| Login                             | POST   | `/login`                                              |
| Listar licitaciones                | GET    | `/licitaciones/`                                      |
| Detalle de licitación               | GET    | `/licitaciones/{id}`                                  |
| Crear licitación                    | POST   | `/licitaciones/`                                      |
| Cambiar estado                      | POST   | `/licitaciones/{id}/estado/{nuevo_estado}`            |
| Agregar producto                    | POST   | `/licitaciones/{id}/productos`                        |
| Eliminar producto                   | DELETE | `/licitaciones/{id}/productos/{producto_id}`          |
| Subir archivo                       | POST   | `/upload/`                                            |
| Vincular documento a licitación      | POST   | `/licitaciones/{id}/documento`                        |
| Historial de cambios                 | GET    | `/licitaciones/{id}/historial`                        |

## Notas de adaptación

- Los nombres de campos usados en los formularios (`titulo`, `entidad`,
  `presupuesto`, `fecha_cierre`, `nombre`, `cantidad`, `precio_unitario`, etc.)
  son suposiciones razonables sobre el esquema del backend. Ajusta los payloads
  en `src/api/licitaciones.js` y los formularios correspondientes a los nombres
  reales de tus modelos Pydantic/SQLAlchemy.
- El endpoint de eliminar producto se asumió como
  `DELETE /licitaciones/{id}/productos/{producto_id}`; cámbialo en
  `src/api/licitaciones.js` si tu backend usa otra ruta.
- `subirArchivo` asume que `/upload/` devuelve un objeto con `url`, `path` o
  `filename`; ajusta esa línea según la respuesta real de tu endpoint.
