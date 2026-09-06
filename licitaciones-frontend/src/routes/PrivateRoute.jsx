import { Navigate, Outlet, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";
import useTokenRefresher from "../components/refresh/useTokenRefresher.jsx";

export default function PrivateRoute() {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  useTokenRefresher();

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  if (adminOnly) {
    const usuarioRol = localStorage.getItem("usuario_rol");
    if (usuarioRol !== "admin") {
      // Si no es admin, lo mandamos al inicio o a una página de acceso denegado
      return <Navigate to="/login" replace />;
    }
  }

  return <Outlet />;
}
