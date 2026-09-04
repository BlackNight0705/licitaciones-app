import { useState } from "react";
import { useNavigate, useLocation, Navigate } from "react-router-dom";
import { FileText, Loader2, AlertCircle } from "lucide-react";
import { useAuth } from "../context/AuthContext.jsx";

export default function LoginPage() {
  const { login, isLoading, error, isAuthenticated } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();
  const location = useLocation();

  if (isAuthenticated) {
    const redirectTo = location.state?.from?.pathname || "/";
    return <Navigate to={redirectTo} replace />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    const success = await login(username, password);
    if (success) {
      navigate(location.state?.from?.pathname || "/", { replace: true });
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-gradient-to-br from-brand-50 via-white to-brand-100 px-4">
      <div className="w-full max-w-md">
        <div className="mb-8 flex flex-col items-center text-center">
          <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-xl bg-brand-800">
            <FileText size={22} className="text-white" />
          </div>
          <h1 className="font-display text-2xl font-semibold text-ink-900">
            Portal de Licitaciones
          </h1>
          <p className="mt-1.5 text-sm text-ink-500">
            Inicia sesión para gestionar tus procesos
          </p>
        </div>

        <form onSubmit={handleSubmit} className="card space-y-4 p-7">
          {error && (
            <div className="flex items-start gap-2 rounded-lg bg-rose-50 px-3.5 py-2.5 text-sm text-rose-700">
              <AlertCircle size={16} className="mt-0.5 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div>
            <label htmlFor="username" className="label-field">
              Usuario o correo
            </label>
            <input
              id="username"
              type="text"
              autoComplete="username"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="input-field"
              placeholder="tu.usuario@empresa.com"
            />
          </div>

          <div>
            <label htmlFor="password" className="label-field">
              Contraseña
            </label>
            <input
              id="password"
              type="password"
              autoComplete="current-password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="input-field"
              placeholder="••••••••"
            />
          </div>

          <button type="submit" disabled={isLoading} className="btn-primary w-full">
            {isLoading && <Loader2 size={16} className="animate-spin" />}
            {isLoading ? "Verificando..." : "Iniciar sesión"}
          </button>
        </form>
      </div>
    </div>
  );
}
