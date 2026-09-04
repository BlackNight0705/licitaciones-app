import { createContext, useContext, useState, useEffect } from "react";
import axiosClient from "../api/axiosClient";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const usuarioRol = localStorage.getItem("usuario_rol");
    const usuarioEmail = localStorage.getItem("usuario_email");
    if (usuarioRol) {
      setUser({ rol: usuarioRol, email: usuarioEmail });
    }
    setLoading(false);
  }, []);

  const login = async (username, password) => {
    const body = new URLSearchParams();
    body.append("username", username);
    body.append("password", password);

    const { data } = await axiosClient.post("/login", body, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });

    localStorage.setItem("usuario_rol", data.usuario_rol);
    localStorage.setItem("usuario_email", data.usuario_email);
    setUser({ rol: data.usuario_rol, email: data.usuario_email });
    return data;
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

  // Definimos isAuthenticated y mapeamos loading como isLoading para compatibilidad con LoginPage
  const isAuthenticated = !!user;
  const isLoading = loading;

  return (
    <AuthContext.Provider value={{ user, login, logout, loading, isLoading, isAuthenticated }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);