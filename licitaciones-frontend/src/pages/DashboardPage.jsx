import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Plus, Loader2, AlertCircle, Inbox, ChevronRight, UserPlus, Building2, Trash2 } from "lucide-react";
import Badge from "../components/ui/Badge.jsx";
import LicitacionForm from "../components/licitaciones/LicitacionForm.jsx";
import UsuarioForm from "../components/usuario/UsuarioForm.jsx";
import ClienteForm from "../components/cliente/ClienteForm.jsx";
import { getLicitaciones, eliminarLicitacion } from "../api/licitaciones.js";
// Asegúrate de importar tu función para eliminar si la tienes en la API, o haz el fetch directamente:
// import { getLicitaciones, deleteLicitacion } from "../api/licitaciones.js";

export default function DashboardPage() {
  const [licitaciones, setLicitaciones] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isFormOpen, setIsFormOpen] = useState(false);
  const [isUserFormOpen, setIsUserFormOpen] = useState(false);
  const [isClienteFormOpen, setIsClienteFormOpen] = useState(false);
  
  // Estado para el usuario actual
  const [usuarioActual, setUsuarioActual] = useState(null);

  const loadLicitaciones = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await getLicitaciones();
      setLicitaciones(Array.isArray(data) ? data : data?.items || []);
    } catch (err) {
      setError(
        err.response?.data?.detail || "No se pudieron cargar las licitaciones."
      );
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadLicitaciones();
    
    const rolGuardado = localStorage.getItem("usuario_rol");
    const emailGuardado = localStorage.getItem("usuario_email");
    
    if (rolGuardado) {
      setUsuarioActual({ rol: rolGuardado, usuario_email: emailGuardado });
    }
  }, []);

  const formatCurrency = (value) =>
    value == null
      ? "—"
      : new Intl.NumberFormat("es-ES", { style: "currency", currency: "USD" }).format(
          value
        );

  // Función para manejar la eliminación de una licitación desde el dashboard
const handleEliminar = async (licId, titulo) => {
    if (!window.confirm(`¿Estás seguro de que deseas eliminar la licitación "${titulo}"? Se borrarán también sus productos, pagos e historial.`)) {
      return;
    }

    try {
      await eliminarLicitacion(licId);
      loadLicitaciones(); // Recarga la tabla de inmediato
    } catch (err) {
      alert(err.response?.data?.detail || "No se pudo eliminar la licitación.");
    }
  };

  // Verificamos si es administrador
  const esAdmin = usuarioActual?.rol === "admin" || usuarioActual?.usuario_rol === "admin";

  return (
    <div>
      <div className="mb-6 flex flex-wrap items-center justify-between gap-4">
        <div>
          <p className="text-sm text-ink-500">
            {licitaciones.length} proceso{licitaciones.length !== 1 && "s"} registrado
            {licitaciones.length !== 1 && "s"}
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          {esAdmin && (
            <>
              <button
                type="button"
                onClick={() => setIsClienteFormOpen(true)}
                className="btn-secondary flex items-center gap-2"
              >
                <Building2 size={18} />
                Registrar cliente
              </button>

              <button
                type="button"
                onClick={() => setIsUserFormOpen(true)}
                className="btn-secondary flex items-center gap-2"
              >
                <UserPlus size={18} />
                Registrar usuario
              </button>
            </>
          )}

          <button
            type="button"
            onClick={() => setIsFormOpen(true)}
            className="btn-primary flex items-center gap-2"
          >
            <Plus size={18} />
            Nueva licitación
          </button>
        </div>
      </div>

      {isLoading && (
        <div className="card flex items-center justify-center gap-2 py-16 text-ink-500">
          <Loader2 size={18} className="animate-spin" />
          Cargando licitaciones...
        </div>
      )}

      {!isLoading && error && (
        <div className="card flex items-center gap-2.5 px-5 py-4 text-sm text-rose-700">
          <AlertCircle size={18} />
          {error}
        </div>
      )}

      {!isLoading && !error && licitaciones.length === 0 && (
        <div className="card flex flex-col items-center gap-3 py-16 text-center">
          <Inbox size={32} className="text-brand-300" />
          <div>
            <p className="font-medium text-ink-900">Todavía no hay licitaciones</p>
            <p className="text-sm text-ink-500">
              Crea la primera para empezar a darle seguimiento.
            </p>
          </div>
        </div>
      )}

      {!isLoading && !error && licitaciones.length > 0 && (
        <div className="card overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead className="border-b border-brand-100 bg-brand-50/60 text-xs uppercase tracking-wide text-ink-500">
                <tr>
                  <th className="px-5 py-3 font-medium">Título</th>
                  <th className="px-5 py-3 font-medium">Entidad</th>
                  <th className="px-5 py-3 font-medium">Presupuesto</th>
                  <th className="px-5 py-3 font-medium">Estado</th>
                  <th className="px-5 py-3 text-right font-medium">Acciones</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-brand-100">
                {licitaciones.map((lic) => {
                  const licId = lic.id ?? lic.licitacion_id;
                  const titulo = lic.titulo ?? lic.licitacion_titulo;
                  const entidad = lic.cliente?.cliente_nombre ?? lic.entidad ?? lic.licitacion_entidad;
                  const presupuesto = lic.presupuesto ?? lic.licitacion_presupuesto_maximo;
                  const estado = lic.estado ?? lic.licitacion_estado;

                  return (
                    <tr key={licId} className="transition-colors hover:bg-brand-50/50">
                      <td className="px-5 py-3.5 font-medium text-ink-900">
                        {titulo}
                      </td>
                      <td className="px-5 py-3.5 text-ink-500">{entidad || "—"}</td>
                      <td className="px-5 py-3.5 text-ink-500">
                        {formatCurrency(presupuesto)}
                      </td>
                      <td className="px-5 py-3.5">
                        <Badge estado={estado} />
                      </td>
                      <td className="px-5 py-3.5 text-right">
                        <div className="flex items-center justify-end gap-3">
                          <Link
                            to={`/licitaciones/${licId}`}
                            className="inline-flex items-center gap-1 text-sm font-medium text-brand-700 hover:text-brand-900"
                          >
                            Ver detalle
                            <ChevronRight size={16} />
                          </Link>

                          {/* Botón de eliminar integrado en la tabla */}
                          <button
                            type="button"
                            onClick={() => handleEliminar(licId, titulo)}
                            className="text-rose-600 hover:text-rose-800 transition-colors"
                            title="Eliminar licitación"
                          >
                            <Trash2 size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Modal para crear licitaciones */}
      <LicitacionForm
        isOpen={isFormOpen}
        onClose={() => setIsFormOpen(false)}
        onCreated={(nueva) => setLicitaciones((prev) => [nueva, ...prev])}
      />

      {/* Modales protegidos para administradores */}
      {esAdmin && (
        <>
          <UsuarioForm
            isOpen={isUserFormOpen}
            onClose={() => setIsUserFormOpen(false)}
            onCreated={(nuevo) => {
              console.log("Usuario creado correctamente:", nuevo);
            }}
          />

          <ClienteForm
            isOpen={isClienteFormOpen}
            onClose={() => setIsClienteFormOpen(false)}
            onCreated={(nuevo) => {
              console.log("Cliente creado correctamente:", nuevo);
            }}
          />
        </>
      )}
    </div>
  );
}