import { useEffect, useState } from "react";
import api from "../api/axiosClient";

export default function AdminAuditPage() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        const response = await api.get("/api/admin/auditorias");
        setLogs(response.data);
      } catch (err) {
        setError(err.response?.data?.detail || "No tienes permisos para ver la bitácora de auditoría.");
      } finally {
        setLoading(false);
      }
    };
    fetchLogs();
  }, []);

  if (loading) return <div className="p-6 text-gray-600">Cargando bitácora de auditoría...</div>;
  if (error) return <div className="p-6 text-red-500 font-semibold">{error}</div>;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Bitácora de Auditoría del Sistema</h1>
      </div>
      <div className="overflow-x-auto bg-white shadow-md rounded-lg border border-gray-200">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Fecha y Hora</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Usuario ID</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Módulo</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Acción</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Detalles</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {logs.map((log) => (
              <tr key={log.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-xs text-gray-500">
                  {new Date(log.fecha_hora).toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                  {log.usuario_id || "Sistema"}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{log.modulo}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-semibold text-indigo-600">{log.accion}</td>
                <td className="px-6 py-4 text-sm text-gray-600">{log.detalles}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}