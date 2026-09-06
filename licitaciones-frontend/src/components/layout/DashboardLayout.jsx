import { useState,useEffect } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "./Sidebar.jsx";
import Navbar from "./Navbar.jsx";
import axiosClient from '../../api/axiosClient.js'; // Asegúrate de que la ruta sea correcta según tu estructura de carpetas

export default function DashboardLayout({ title }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  // Intervalo para refrescar el token cada 20 minutos
  useEffect(() => {
    const REFRESH_INTERVAL = 2 * 60 * 1000; 

    const intervalId = setInterval(async () => {
      try {
        await axiosClient.post("/auth/refresh");
      } catch (error) {
        // Si el refresh falla (cookie vencida), el interceptor ya redirige, 
        // pero esta es una red de seguridad extra:
        navigate("/login", { replace: true });
      }
    }, REFRESH_INTERVAL);

    // Limpia el intervalo al desmontar el layout (cuando el usuario cierra sesión)
    return () => clearInterval(intervalId);
  }, [navigate]);

  return (
    <div className="min-h-screen bg-brand-50 flex">
      <Sidebar isOpen={sidebarOpen} onNavigate={() => setSidebarOpen(false)} />

      {sidebarOpen && (
        <div
          className="fixed inset-0 z-30 bg-ink-900/30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
          aria-hidden="true"
        />
      )}

      <div className="flex-1 flex flex-col min-w-0">
        <Navbar title={title} onMenuClick={() => setSidebarOpen(true)} />
        <main className="flex-1 p-4 lg:p-8 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}