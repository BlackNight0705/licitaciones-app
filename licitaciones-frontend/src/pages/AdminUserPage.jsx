import { useEffect, useState } from "react";
import api from '../../api/axiosClient';

export default function AdminUsersPage() {
  const [usuarios, setUsuarios] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchUsuarios = async () => {
      try {
        const response = await api.get("/api/admin/usuarios");
        setUsuarios(response.data);
      } catch (err) {
        setError(err.response?.data?.detail || "No tienes permisos o ocurrió un error al cargar los usuarios.");
      } finally {
        setLoading(false);
      }
    };
    fetchUsuarios();
  }, []);

  if (loading) return <div className="p-6 text-gray-600">Cargando usuarios...</div>;
  if (error) return <div className="p-6 text-red-500 font-semibold">{error}</div>;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Gestión de Usuarios y Clientes</h1>
      </div>
      <div className="overflow-x-auto bg-white shadow-md rounded-lg border border-gray-200">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Correo</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Rol</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {usuarios.map((u) => (
              <tr key={u.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{u.id}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{u.email}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm">
                  <span className={`px-2.5 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                    u.rol === 'admin' ? 'bg-purple-100 text-purple-800' : 'bg-green-100 text-green-800'
                  }`}>
                    {u.rol}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}