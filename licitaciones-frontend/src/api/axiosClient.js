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
// Interceptor de response: si la sesión expiró o es inválida (401),
// limpia cualquier dato de UI (como el rol) y redirige al login.
axiosClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("usuario_rol");
      localStorage.removeItem("usuario_email");
      if (window.location.pathname !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default axiosClient;