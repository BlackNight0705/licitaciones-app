import { useEffect, useState } from "react";
import api from '../api/axiosClient';
import UsuarioForm from "./usuarioform.jsx";
import ClienteForm from "./ClienteForm.jsx";
import { Loader2 } from "lucide-react";

export default function AdminUsersPage() {
  const [activeTab, setActiveTab] = useState("usuarios"); // "usuarios" o "clientes"
  const [usuarios, setUsuarios] = useState([]);
  const [clientes, setClientes] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Estados para controlar los Modales de Edición y los mensajes de éxito/error
  const [editingUsuario, setEditingUsuario] = useState(null);
  const [editingCliente, setEditingCliente] = useState(null);
  const [modalMessage, setModalMessage] = useState("");

  // Estados para los modales de creación
  const [isUsuarioModalOpen, setIsUsuarioModalOpen] = useState(false);
  const [isClienteModalOpen, setIsClienteModalOpen] = useState(false);

  const fetchData = async () => {
    setLoading(true);
    setError(null);

    try {
      const [resUsuarios, resClientes] = await Promise.allSettled([
        api.get("/admin/usuarios/"), 
        api.get("/admin/clientes/")
      ]);
      
      if (resUsuarios.status === "fulfilled") {
        const data = resUsuarios.value.data;
        setUsuarios(Array.isArray(data) ? data : data?.items || []);
      } else {
        console.warn("No se pudieron cargar los usuarios:", resUsuarios.reason);
        setUsuarios([]);
      }

      if (resClientes.status === "fulfilled") {
        const data = resClientes.value.data;
        setClientes(Array.isArray(data) ? data : data?.items || []);
      } else {
        console.warn("No se pudieron cargar los clientes:", resClientes.reason);
        setClientes([]);
      }

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

  useEffect(() => {
    fetchData();
  }, []);

  // --- ACCIONES DE USUARIO ---
  const handleUpdateUsuarioSubmit = async (e) => {
    e.preventDefault();
    const id = editingUsuario.id ?? editingUsuario.usuario_id;
    try {
      const payload = {
        usuario_nombre: editingUsuario.nombre ?? editingUsuario.usuario_nombre,
        usuario_email: editingUsuario.email ?? editingUsuario.usuario_email,
        usuario_rol: editingUsuario.rol ?? editingUsuario.usuario_rol,
      };
      if (editingUsuario.nueva_password) {
        payload.usuario_password = editingUsuario.nueva_password;
      }

      await api.put(`/admin/usuarios/${id}`, payload);
      setEditingUsuario(null);
      setModalMessage("Usuario actualizado correctamente.");
      fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || "Error al actualizar el usuario.");
    }
  };

  const handleToggleEstadoUsuario = async (u) => {
    const id = u.id ?? u.usuario_id;
    const email = u.email ?? u.usuario_email;
    const activoActual = u.activo ?? u.usuario_estado ?? true;
    const accionTexto = activoActual ? "¿Estás seguro de desactivar" : "¿Estás seguro de activar";
    
    if (!window.confirm(`${accionTexto} al usuario ${email}?`)) return;

    try {
      await api.patch(`/admin/usuarios/${id}/desactivar`);
      setModalMessage(`Estado del usuario actualizado correctamente.`);
      fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || "Error al cambiar el estado del usuario.");
    }
  };

  // --- ACCIONES DE CLIENTE ---
  const handleUpdateClienteSubmit = async (e) => {
    e.preventDefault();
    const id = editingCliente.id ?? editingCliente.cliente_id;
    try {
      const payload = {
        cliente_nombre: editingCliente.nombre ?? editingCliente.cliente_nombre,
        cliente_email: (editingCliente.email ?? editingCliente.cliente_email) || "",
        cliente_telefono: (editingCliente.telefono ?? editingCliente.cliente_telefono) || "",
        cliente_empresa: (editingCliente.empresa ?? editingCliente.cliente_empresa) || "",
      };

      await api.put(`/admin/clientes/${id}`, payload);
      setEditingCliente(null);
      setModalMessage("Cliente actualizado correctamente.");
      fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || "Error al actualizar el cliente.");
    }
  };

  const handleToggleEstadoCliente = async (c) => {
    const id = c.id ?? c.cliente_id;
    const nombre = c.nombre ?? c.cliente_nombre;
    const activoActual = c.activo ?? c.cliente_estado ?? true;
    const accionTexto = activoActual ? "¿Estás seguro de desactivar" : "¿Estás seguro de activar";

    if (!window.confirm(`${accionTexto} al cliente ${nombre}?`)) return;

    try {
      await api.patch(`/admin/clientes/${id}/estado`);
      setModalMessage(`Estado del cliente actualizado correctamente.`);
      fetchData();
    } catch (err) {
      alert(err.response?.data?.detail || "Error al cambiar el estado del cliente.");
    }
  };

  if (loading) return <div className="p-6 text-gray-600">Cargando información...</div>;
  if (error) return <div className="p-6 text-red-500 font-semibold">{error}</div>;

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-800">Gestión de Usuarios y Clientes</h1>
        <div>
          {activeTab === "usuarios" ? (
            <button
              onClick={() => setIsUsuarioModalOpen(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition"
            >
              Registrar usuario
            </button>
          ) : (
            <button
              onClick={() => setIsClienteModalOpen(true)}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition"
            >
              Registrar cliente
            </button>
          )}
        </div>
      </div>

      {modalMessage && (
        <div className="mb-4 p-4 bg-green-100 text-green-700 rounded-lg flex justify-between items-center">
          <span>{modalMessage}</span>
          <button onClick={() => setModalMessage("")} className="font-bold text-green-900">&times;</button>
        </div>
      )}

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
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {usuarios.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-6 py-4 text-center text-sm text-gray-500">No hay usuarios registrados.</td>
                </tr>
              ) : (
                usuarios.map((u) => {
                  const estaActivo = u.activo ?? u.usuario_estado ?? true;
                  return (
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
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`px-2.5 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          estaActivo ? 'bg-emerald-100 text-emerald-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {estaActivo ? 'Activo' : 'Inactivo'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                        <button
                          onClick={() => setEditingUsuario({ ...u })}
                          className="text-blue-600 hover:text-blue-900 bg-blue-50 px-3 py-1 rounded"
                        >
                          Editar
                        </button>
                        <button
                          onClick={() => handleToggleEstadoUsuario(u)}
                          className={`${
                            estaActivo 
                              ? 'text-amber-600 hover:text-amber-900 bg-amber-50' 
                              : 'text-emerald-600 hover:text-emerald-900 bg-emerald-50'
                          } px-3 py-1 rounded`}
                        >
                          {estaActivo ? 'Desactivar' : 'Activar'}
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">ID</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Nombre</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Estado</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Acciones</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {clientes.length === 0 ? (
                <tr>
                  <td colSpan="4" className="px-6 py-4 text-center text-sm text-gray-500">No hay clientes registrados.</td>
                </tr>
              ) : (
                clientes.map((c) => {
                  const estaActivo = c.activo ?? c.cliente_estado ?? true;
                  return (
                    <tr key={c.id ?? c.cliente_id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{c.id ?? c.cliente_id}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{c.nombre ?? c.cliente_nombre}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span className={`px-2.5 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                          estaActivo ? 'bg-emerald-100 text-emerald-800' : 'bg-gray-100 text-gray-800'
                        }`}>
                          {estaActivo ? 'Activo' : 'Inactivo'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium space-x-2">
                        <button
                          onClick={() => setEditingCliente({ ...c })}
                          className="text-blue-600 hover:text-blue-900 bg-blue-50 px-3 py-1 rounded"
                        >
                          Editar
                        </button>
                        <button
                          onClick={() => handleToggleEstadoCliente(c)}
                          className={`${
                            estaActivo 
                              ? 'text-amber-600 hover:text-amber-900 bg-amber-50' 
                              : 'text-emerald-600 hover:text-emerald-900 bg-emerald-50'
                          } px-3 py-1 rounded`}
                        >
                          {estaActivo ? 'Desactivar' : 'Activar'}
                        </button>
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        )}
      </div>

      {/* MODAL EDITAR USUARIO */}
      {editingUsuario && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6 shadow-xl">
            <h2 className="text-xl font-bold mb-4 text-gray-800">Editar Usuario</h2>
            <form onSubmit={handleUpdateUsuarioSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Nombre</label>
                <input
                  type="text"
                  value={editingUsuario.nombre ?? editingUsuario.usuario_nombre ?? ""}
                  onChange={(e) => setEditingUsuario({ ...editingUsuario, nombre: e.target.value, usuario_nombre: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md p-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Correo Electrónico</label>
                <input
                  type="email"
                  value={editingUsuario.email ?? editingUsuario.usuario_email ?? ""}
                  onChange={(e) => setEditingUsuario({ ...editingUsuario, email: e.target.value, usuario_email: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md p-2 text-sm"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Rol</label>
                <select
                  value={editingUsuario.rol ?? editingUsuario.usuario_rol ?? "usuario"}
                  onChange={(e) => setEditingUsuario({ ...editingUsuario, rol: e.target.value, usuario_rol: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md p-2 text-sm"
                >
                  <option value="usuario">usuario</option>
                  <option value="admin">admin</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Nueva Contraseña (Opcional)</label>
                <input
                  type="password"
                  placeholder="Dejar en blanco para no cambiar"
                  value={editingUsuario.nueva_password || ""}
                  onChange={(e) => setEditingUsuario({ ...editingUsuario, nueva_password: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md p-2 text-sm"
                />
              </div>
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setEditingUsuario(null)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm text-gray-700 hover:bg-gray-100"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700"
                >
                  Guardar Cambios
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODAL EDITAR CLIENTE */}
      {editingCliente && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6 shadow-xl">
            <h2 className="text-xl font-bold mb-4 text-gray-800">Editar Cliente</h2>
            <form onSubmit={handleUpdateClienteSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Nombre del Cliente</label>
                <input
                  type="text"
                  value={editingCliente.nombre ?? editingCliente.cliente_nombre ?? ""}
                  onChange={(e) => setEditingCliente({ ...editingCliente, nombre: e.target.value, cliente_nombre: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md p-2 text-sm"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Correo</label>
                <input
                  type="email"
                  value={editingCliente.email ?? editingCliente.cliente_email ?? ""}
                  onChange={(e) => setEditingCliente({ ...editingCliente, email: e.target.value, cliente_email: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md p-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Teléfono</label>
                <input
                  type="text"
                  value={editingCliente.telefono ?? editingCliente.cliente_telefono ?? ""}
                  onChange={(e) => setEditingCliente({ ...editingCliente, telefono: e.target.value, cliente_telefono: e.target.value })}
                  className="mt-1 block w-full border border-gray-300 rounded-md p-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700">Empresa</label>
                <input
                  type="text"
                  value={editingCliente.empresa ?? editingCliente.cliente_empresa ?? ""}
                  onChange={(e) => setEditingCliente({ ...editingChange => ({ ...editingCliente, empresa: e.target.value, cliente_empresa: e.target.value }) })}
                  className="mt-1 block w-full border border-gray-300 rounded-md p-2 text-sm"
                />
              </div>
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setEditingCliente(null)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm text-gray-700 hover:bg-gray-100"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700"
                >
                  Guardar Cambios
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* MODALES DE CREACIÓN */}
      <UsuarioForm
        isOpen={isUsuarioModalOpen}
        onClose={() => setIsUsuarioModalOpen(false)}
        onCreated={() => {
          setModalMessage("Usuario registrado correctamente.");
          fetchData();
        }}
      />

      <ClienteForm
        isOpen={isClienteModalOpen}
        onClose={() => setIsClienteModalOpen(false)}
        onCreated={() => {
          setModalMessage("Cliente registrado correctamente.");
          fetchData();
        }}
      />
    </div>
  );
}