import { createContext, useContext, useState, useEffect } from "react";
import axiosClient from "../api/axiosClient";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null); // <-- Estado para el mensaje de error

  useEffect(() => {
    const usuarioRol = localStorage.getItem("usuario_rol");
    const usuarioEmail = localStorage.getItem("usuario_email");
    if (usuarioRol) {
      setUser({ rol: usuarioRol, email: usuarioEmail });
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    setError(null); // Limpiamos errores previos al reintentar
    const body = new URLSearchParams();
    body.append("username", username);
    body.append("password", password);

    try {
      const { data } = await axiosClient.post("/login", body, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      localStorage.setItem("usuario_rol", data.usuario_rol);
      localStorage.setItem("usuario_email", data.usuario_email);
      setUser({ rol: data.usuario_rol, email: data.usuario_email });
      return true; // Retornamos true indicando éxito
    } catch (err) {
      // Capturamos el error del backend o de red y definimos un mensaje amigable
      if (err.response) {
        if (err.response.status === 401) {
          setError("Usuario o contraseña incorrectos.");
        } else if (err.response.data && err.response.data.detail) {
          setError(err.response.data.detail);
        } else {
          setError("Ocurrió un error en el servidor. Inténtalo más tarde.");
        }
      } else {
        setError("No se pudo conectar con el servidor. Verifica tu conexión.");
      }
      return false; // Retornamos false indicando que falló
    }
  };

  const logout = async () => {
    try {
      await axiosClient.post("/logout");
    } catch (e) {
      // Ignorar errores de red al cerrar sesión
    }
    localStorage.removeItem("usuario_rol");
    localStorage.removeItem("usuario_email");
    setUser(null);
    window.location.href = "/login";
  };

  const isAuthenticated = !!user;
  const isLoading = loading;

  return (
    <AuthContext.Provider value={{ user, login, logout, loading, isLoading, isAuthenticated, error }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);