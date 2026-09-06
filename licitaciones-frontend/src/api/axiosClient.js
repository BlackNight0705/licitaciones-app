import axios from "axios";

export const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const axiosClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

// Variables para el refresh token...
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

axiosClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // 1. INTERCEPTOR PARA ERRORES DE VALIDACIÓN (Pydantic 422 o Bad Request 400)
    if (error.response && (error.response.status === 422 || error.response.status === 400)) {
      const detalle = error.response.data.detail;
      
      let mensajeError = "Datos inválidos.";
      
      // Si Pydantic manda un arreglo de errores detallados
      if (Array.isArray(detalle)) {
        mensajeError = detalle.map(e => {
          const campo = e.loc[e.loc.length - 1];
          return `- [${campo}]: ${e.msg}`;
        }).join("\n");
      } else if (typeof detalle === "string") {
        mensajeError = detalle;
      }

      // Rechazamos la promesa pero con un Error limpio que ya trae el mensaje formateado
      return Promise.reject(new Error(mensajeError));
    }

    // 2. TU LÓGICA EXISTENTE PARA TOKENS 401 (Refresh token)
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (originalRequest.url.includes("/login") || originalRequest.url.includes("/refresh")) {
        localStorage.removeItem("usuario_rol");
        localStorage.removeItem("usuario_email");
        if (window.location.pathname !== "/login") {
          window.location.href = "/login";
        }
        return Promise.reject(error);
      }

      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then(() => axiosClient(originalRequest))
          .catch((err) => Promise.reject(err));
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        await axiosClient.post("/auth/refresh");
        processQueue(null);
        isRefreshing = false;
        return axiosClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        isRefreshing = false;
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