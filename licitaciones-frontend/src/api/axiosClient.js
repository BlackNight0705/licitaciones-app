import axios from "axios";

// URL base del backend FastAPI. Configurable vía variable de entorno.
export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const axiosClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  // OBLIGATORIO: Permite que el navegador envíe y reciba las cookies HttpOnly automáticamente
  withCredentials: true,
});

// Variables para controlar la cola de peticiones mientras se renueva el token
let isRefreshing = false;
let failedQueue = [];

const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  failedQueue = [];
};

// Interceptor de respuesta para manejar la expiración y renovación del token
axiosClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Si el error es 401 y no hemos intentado reintentar esta petición aún
    if (error.response?.status === 401 && !originalRequest._retry) {
      
      // Evitamos bucles infinitos si el propio endpoint de refresh o el login fallan con 401
      if (originalRequest.url.includes("/login") || originalRequest.url.includes("/refresh")) {
        localStorage.removeItem("usuario_rol");
        localStorage.removeItem("usuario_email");
        if (window.location.pathname !== "/login") {
          window.location.href = "/login";
        }
        return Promise.reject(error);
      }

      if (isRefreshing) {
        // Si ya hay una petición refrescando el token, encolamos las demás
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then(() => {
            return axiosClient(originalRequest);
          })
          .catch((err) => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        // Llamada al endpoint de refresco en tu FastAPI. 
        // Como usa cookies HttpOnly, el navegador enviará automáticamente la cookie de refresh.
        // Ajusta la ruta "/auth/refresh" o "/token/refresh" según tu backend.
        await axiosClient.post("/auth/refresh"); 

        processQueue(null);
        isRefreshing = false;

        // Reintentamos la petición original que dio 401
        return axiosClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        isRefreshing = false;

        // Si el refresh token también expiró o es inválido, limpiamos y mandamos al login
        localStorage.removeItem("usuario_rol");
        localStorage.removeItem("usuario_email");
        if (window.location.pathname !== "/login") {
          window.location.href = "/login";
        }
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default axiosClient;