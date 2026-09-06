import { useEffect, useState } from "react";
import api from '../api/axiosClient';

export default function AdminUsersPage() {
  const [activeTab, setActiveTab] = useState("usuarios"); // "usuarios" o "clientes"
  const [usuarios, setUsuarios] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);

      try {
        // Ejecutamos ambas peticiones en paralelo de forma independiente usando allSettled
        const [resUsuarios, resClientes] = await Promise.allSettled([
          api.get("/usuarios/"), // O la ruta correspondiente en tu backend
          api.get("/cliente/")
        ]);
        
        // Procesamos usuarios de forma segura
        if (resUsuarios.status === "fulfilled") {
          const data = resUsuarios.value.data;
          setUsuarios(Array.isArray(data) ? data : data?.items || []);
        } else {
          console.warn("No se pudieron cargar los usuarios:", resUsuarios.reason);
          setUsuarios([]);
        }

        // Procesamos clientes de forma segura
        if (resClientes.status === "fulfilled") {
          const data = resClientes.value.data;
          setClientes(Array.isArray(data) ? data : data?.items || []);
        } else {
          console.warn("No se pudieron cargar los clientes:", resClientes.reason);
          setClientes([]);
        }

        // Si ambas fallaron, mostramos un error general
        if (resUsuarios.status === "rejected" && resClientes.status === "rejected") {
          const errDetail = resUsuarios.reason.response?.data?.detail || resClientes.reason.response?.data?.detail || "No tienes permisos o ocurrió un error al cargar los datos.";
          setError(errDetail);
        }

      } catch (err) {
        setError(err.response?.data?.detail || "No tienes permisos o ocurrió un error al cargar los datos.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <div className="p-6 text-gray-600">Cargando información...</div>;
  if (error) return <div className="p-6 text-red-500 font-semibold">{error}</div>;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Gestión de Usuarios y Clientes</h1>
      </div>

      {/* Pestañas de navegación interna */}
      <div className="flex border-b border-gray-200 mb-6">
        <button
          onClick={() => setActiveTab("usuarios")}
          className={`py-2 px-4 font-medium border-b-2 text-sm ${
            activeTab === "usuarios"
              ? "border-blue-600 text-blue-600"
              : "border-transparent text-gray-500 hover:text-gray-700"
          }`}
        >
          Usuarios ({usuarios.length})
        </button>
        <button
          onClick={() => setActiveTab("clientes")}
          className={`py-2 px-4 font-medium border-b-2 text-sm ${
            activeTab === "clientes"
              ? "border-blue-600 text-blue-600"
              : "border-transparent text-gray-500 hover:text-gray-700"
          }`}
        >
          Clientes ({clientes.length})
        </button>
      </div>

      {/* Contenido condicional según la pestaña activa */}
      <div className="overflow-x-auto bg-white shadow-md rounded-lg border border-gray-200">
        {activeTab === "usuarios" ? (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Correo</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rol</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {usuarios.length === 0 ? (
                <tr>
                  <td colSpan="3" className="px-6 py-4 text-center text-sm text-gray-500">No hay usuarios registrados.</td>
                </tr>
              ) : (
                usuarios.map((u) => (
                  <tr key={u.id ?? u.usuario_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{u.id ?? u.usuario_id}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{u.email ?? u.usuario_email}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`px-2.5 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        (u.rol ?? u.usuario_rol) === 'admin' ? 'bg-purple-100 text-purple-800' : 'bg-green-100 text-green-800'
                      }`}>
                        {u.rol ?? u.usuario_rol}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nombre</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {clientes.length === 0 ? (
                <tr>
                  <td colSpan="2" className="px-6 py-4 text-center text-sm text-gray-500">No hay clientes registrados.</td>
                </tr>
              ) : (
                clientes.map((c) => (
                  <tr key={c.id ?? c.cliente_id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{c.id ?? c.cliente_id}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{c.nombre ?? c.cliente_nombre}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}