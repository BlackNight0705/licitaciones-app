import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { ArrowLeft, Loader2, AlertCircle, Calendar, Building2, Save, Edit2, Trophy, XCircle } from "lucide-react";
import Badge from "../components/ui/Badge.jsx";
import ProductoForm from "../components/productos/ProductoForm.jsx";
import ProductoList from "../components/productos/ProductoList.jsx";
import UploadDocumento from "../components/documentos/UploadDocumento.jsx";
import HistorialList from "../components/historial/HistorialList.jsx";
import SeccionPagosModal from "../components/pagos/SeccionPagosModal.jsx";
import { getLicitacion, getHistorial, actualizarLicitacion } from "../api/licitaciones.js";

export default function LicitacionDetailPage() {
  const { id } = useParams();
  const [licitacion, setLicitacion] = useState(null);
  const [historial, setHistorial] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  
  const [isEditingActive, setIsEditingActive] = useState(false);
  const [mensajeNotificacion, setMensajeNotificacion] = useState(null);
  const [isConfirmingDoc, setIsConfirmingDoc] = useState(false);
  
  // Estados de confirmación para ganar o perder
  const [isConfirmingPerdida, setIsConfirmingPerdida] = useState(false);
  const [isConfirmingGanada, setIsConfirmingGanada] = useState(false);

  const [formData, setFormData] = useState({
    licitacion_titulo: "",
    licitacion_descripcion: "",
    licitacion_presupuesto_maximo: "",
    licitacion_fecha_limite: "",
    licitacion_cliente_id: "",
  });

  const mostrarAlerta = (texto, tipo = "success") => {
    setMensajeNotificacion({ texto, tipo });
    setTimeout(() => {
      setMensajeNotificacion(null);
    }, 4000);
  };

  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const [licData, histData] = await Promise.all([
        getLicitacion(id),
        getHistorial(id).catch(() => []),
      ]);
      setLicitacion(licData);
      
      setFormData({
        licitacion_titulo: licData.licitacion_titulo || "",
        licitacion_descripcion: licData.licitacion_descripcion || "",
        licitacion_presupuesto_maximo: licData.licitacion_presupuesto_maximo || "",
        licitacion_fecha_limite: licData.licitacion_fecha_limite ? licData.licitacion_fecha_limite.split("T")[0] : "",
        licitacion_cliente_id: licData.licitacion_cliente_id || "",
      });

      setHistorial(Array.isArray(histData) ? histData : histData?.items || []);
    } catch (err) {
      setError(
        err.response?.data?.detail || "No se pudo cargar la licitación."
      );
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [id]);

  const handleGuardarCambios = async (nuevoEstado = null) => {
    setIsSaving(true);
    try {
      const payload = {
        ...formData,
        licitacion_presupuesto_maximo: formData.licitacion_presupuesto_maximo !== "" 
          ? parseFloat(formData.licitacion_presupuesto_maximo) 
          : 0,
        ...(nuevoEstado && { licitacion_estado: nuevoEstado })
      };

      const licActualizada = await actualizarLicitacion(id, payload);
      setLicitacion(licActualizada);
      setIsEditingActive(false);

      const mensajes = {
        activa: "¡Licitación activada con éxito!",
        ganada: "¡Felicitaciones! Licitación marcada como ganada.",
        perdida: "Licitación marcada como perdida.",
        default: "Cambios guardados correctamente."
      };
      
      mostrarAlerta(mensajes[nuevoEstado] || mensajes.default);
      loadData();
    } catch (err) {
      mostrarAlerta(err.response?.data?.detail || "Error al actualizar la licitación.", "error");
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="card flex items-center justify-center gap-2 py-16 text-ink-500">
        <Loader2 size={18} className="animate-spin" />
        Cargando licitación...
      </div>
    );
  }

  if (error || !licitacion) {
    return (
      <div className="card flex items-center gap-2.5 px-5 py-4 text-sm text-rose-700">
        <AlertCircle size={18} />
        {error || "Licitación no encontrada."}
      </div>
    );
  }

  const formatCurrency = (value) =>
    value == null
      ? "—"
      : new Intl.NumberFormat("es-ES", { style: "currency", currency: "USD" }).format(value);

  const esBorrador = licitacion.licitacion_estado === "borrador";
  const esActiva = licitacion.licitacion_estado === "activa";
  const mostrarFormularioEdicion = esBorrador || (esActiva && isEditingActive);

  // Lógica para determinar el estado financiero actual y renderizar su respectivo badge
  const renderBadgeFinanciero = () => {
    if (licitacion.licitacion_estado !== "ganada" && licitacion.licitacion_estado !== "adjudicada") {
      return null;
    }

    const pagos = licitacion.pagos || [];
    const totalPagado = pagos.reduce((acc, p) => acc + p.pago_monto, 0);
    const presupuesto = licitacion.licitacion_presupuesto_maximo || 0;

    if (totalPagado >= presupuesto && presupuesto > 0) {
      return <Badge estado="pagada" />;
    } else if (totalPagado > 0) {
      return <Badge estado="pago_parcial" />;
    } else {
      return <Badge estado="pendiente_pago" />;
    }
  };

  return (
    <div className="space-y-6 relative">

      {mensajeNotificacion && (
        <div className={`p-4 rounded-lg shadow-md text-sm flex items-center justify-between transition-all ${
          mensajeNotificacion.tipo === "error" 
            ? "bg-rose-50 text-rose-800 border border-rose-200" 
            : "bg-emerald-50 text-emerald-800 border border-emerald-200"
        }`}>
          <span>{mensajeNotificacion.texto}</span>
          <button onClick={() => setMensajeNotificacion(null)} className="font-bold ml-4 text-lg leading-none">&times;</button>
        </div>
      )}

      <div className="flex items-center justify-between">
        <Link to="/" className="inline-flex items-center gap-1.5 text-sm font-medium text-ink-500 hover:text-brand-700">
          <ArrowLeft size={16} /> Volver al listado
        </Link>

        {esActiva && !isEditingActive && (
          <button
            type="button"
            onClick={() => setIsEditingActive(true)}
            className="btn-secondary flex items-center gap-1.5 text-xs py-1.5 px-3"
          >
            <Edit2 size={14} /> Editar licitación
          </button>
        )}
      </div>

      <div className="card p-6">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="w-full md:w-2/3 space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="font-display text-xl font-semibold text-ink-900">
                {licitacion.licitacion_titulo}
              </h2>
              {/* Contenedor de Badges (Estado de Licitación + Estado de Pago) */}
              <div className="flex items-center gap-2">
                <Badge estado={licitacion.licitacion_estado} />
                {renderBadgeFinanciero()}
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-x-4 gap-y-1.5 text-sm text-ink-500">
              <span className="flex items-center gap-1.5">
                <Building2 size={15} />
                {licitacion.cliente?.cliente_nombre || "Entidad no especificada"}
              </span>
              {licitacion.licitacion_fecha_limite && (
                <span className="flex items-center gap-1.5">
                  <Calendar size={15} />
                  Cierra el {new Date(licitacion.licitacion_fecha_limite).toLocaleDateString("es-ES")}
                </span>
              )}
            </div>

            {mostrarFormularioEdicion && (
              <div className="space-y-3 pt-4 border-t border-brand-100">
                <div className="flex justify-between items-center">
                  <h3 className="text-sm font-semibold text-ink-800">
                    {esBorrador ? "Editar información de la licitación" : "Editando licitación activa"}
                  </h3>
                  {esActiva && (
                    <button
                      type="button"
                      onClick={() => { setIsEditingActive(false); loadData(); }}
                      className="text-xs text-ink-400 hover:text-ink-700 underline"
                    >
                      Cancelar
                    </button>
                  )}
                </div>

                <div>
                  <label className="block text-xs font-medium text-ink-500 mb-1">Título</label>
                  <input
                    type="text"
                    value={formData.licitacion_titulo}
                    onChange={(e) => setFormData({ ...formData, licitacion_titulo: e.target.value })}
                    className="w-full border rounded p-2 text-sm"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-ink-500 mb-1">Descripción</label>
                  <textarea
                    value={formData.licitacion_descripcion}
                    onChange={(e) => setFormData({ ...formData, licitacion_descripcion: e.target.value })}
                    className="w-full border rounded p-2 text-sm"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs font-medium text-ink-500 mb-1">Presupuesto Máximo</label>
                    <input
                      type="number"
                      value={formData.licitacion_presupuesto_maximo}
                      onChange={(e) => setFormData({ ...formData, licitacion_presupuesto_maximo: e.target.value })}
                      className="w-full border rounded p-2 text-sm"
                    />
                  </div>
                  <div>
                    <label className="block text-xs font-medium text-ink-500 mb-1">Fecha Límite</label>
                    <input
                      type="date"
                      value={formData.licitacion_fecha_limite}
                      onChange={(e) => setFormData({ ...formData, licitacion_fecha_limite: e.target.value })}
                      className="w-full border rounded p-2 text-sm"
                    />
                  </div>
                </div>

                <div className="flex flex-wrap gap-2 pt-2 items-center">
                  <button
                    type="button"
                    disabled={isSaving}
                    onClick={() => handleGuardarCambios(null)}
                    className="btn-secondary flex items-center gap-1.5 text-xs py-2"
                  >
                    <Save size={14} /> Guardar cambios
                  </button>

                  {esBorrador && (
                    <button
                      type="button"
                      disabled={isSaving}
                      onClick={() => handleGuardarCambios("activa")}
                      className="btn-primary flex items-center gap-1.5 text-xs py-2"
                    >
                      Guardar y Activar
                    </button>
                  )}

                  {esActiva && (
                    <div className="flex flex-wrap gap-2 items-center w-full mt-2 pt-2 border-t border-gray-100">
                      <span className="text-xs font-medium text-ink-500 w-full mb-1">Actualizar resultado de adjudicación:</span>
                      
                      {/* Botón Ganada */}
                      {!isConfirmingGanada ? (
                        <button
                          type="button"
                          disabled={isSaving}
                          onClick={() => setIsConfirmingGanada(true)}
                          className="bg-emerald-600 hover:bg-emerald-700 text-white font-medium px-3 py-2 rounded text-xs flex items-center gap-1.5 transition-colors"
                        >
                          <Trophy size={14} /> Marcar como Ganada
                        </button>
                      ) : (
                        <div className="p-3 bg-emerald-50 border border-emerald-200 rounded-lg text-xs space-y-2 w-full">
                          <p className="text-emerald-800 font-medium">¿Confirmar que esta licitación fue GANADA?</p>
                          <div className="flex items-center gap-2">
                            <button
                              type="button"
                              disabled={isSaving}
                              onClick={async () => {
                                await handleGuardarCambios("ganada");
                                setIsConfirmingGanada(false);
                              }}
                              className="bg-emerald-600 hover:bg-emerald-700 text-white font-medium px-3 py-1.5 rounded transition-colors"
                            >
                              Sí, marcar como ganada
                            </button>
                            <button
                              type="button"
                              disabled={isSaving}
                              onClick={() => setIsConfirmingGanada(false)}
                              className="bg-white border border-gray-300 text-ink-700 hover:bg-gray-50 font-medium px-3 py-1.5 rounded"
                            >
                              Cancelar
                            </button>
                          </div>
                        </div>
                      )}

                      {/* Botón Perdida */}
                      {!isConfirmingPerdida ? (
                        <button
                          type="button"
                          disabled={isSaving}
                          onClick={() => setIsConfirmingPerdida(true)}
                          className="bg-rose-600 hover:bg-rose-700 text-white font-medium px-3 py-2 rounded text-xs flex items-center gap-1.5 transition-colors"
                        >
                          <XCircle size={14} /> Marcar como Perdida
                        </button>
                      ) : (
                        <div className="p-3 bg-rose-50 border border-rose-200 rounded-lg text-xs space-y-2 w-full">
                          <p className="text-rose-800 font-medium">¿Estás seguro de marcar esta licitación como perdida?</p>
                          <div className="flex items-center gap-2">
                            <button
                              type="button"
                              disabled={isSaving}
                              onClick={async () => {
                                await handleGuardarCambios("perdida");
                                setIsConfirmingPerdida(false);
                              }}
                              className="bg-rose-600 hover:bg-rose-700 text-white font-medium px-3 py-1.5 rounded transition-colors"
                            >
                              Sí, marcar como perdida
                            </button>
                            <button
                              type="button"
                              disabled={isSaving}
                              onClick={() => setIsConfirmingPerdida(false)}
                              className="bg-white border border-gray-300 text-ink-700 hover:bg-gray-50 font-medium px-3 py-1.5 rounded"
                            >
                              Cancelar
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          <div className="text-right">
            <p className="text-xs uppercase tracking-wide text-ink-400">Presupuesto</p>
            <p className="text-lg font-semibold text-ink-900">
              {formatCurrency(licitacion.licitacion_presupuesto_maximo)}
            </p>
          </div>
        </div>
      </div>

      {/* Sección de Gestión Financiera y Pagos Integrada */}
      <SeccionPagosModal licitacion={licitacion} onPagoExitoso={loadData} />

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="card p-6">
          <h3 className="mb-4 font-display text-base font-semibold text-ink-900">Productos</h3>
          {mostrarFormularioEdicion && (
            <ProductoForm
              licitacionId={id}
              onAdded={(producto) =>
                setLicitacion((prev) => ({
                  ...prev,
                  productos: [...(prev.productos || []), producto],
                }))
              }
            />
          )}
          <ProductoList
            licitacionId={id}
            productos={licitacion.productos}
            presupuestoMaximo={licitacion.licitacion_presupuesto_maximo}
            readOnly={!mostrarFormularioEdicion}
            onRemoved={(productoId) =>
              setLicitacion((prev) => ({
                ...prev,
                productos: (prev.productos || []).filter((p) => p.id !== productoId && p.licitacion_producto_id !== productoId),
              }))
            }
          />
        </div>

        <div className="card p-6">
          <h3 className="mb-4 font-display text-base font-semibold text-ink-900">Documentos</h3>
          {licitacion.licitacion_documento_url && 
           licitacion.licitacion_documento_url !== "null" && 
           licitacion.licitacion_documento_url.trim() !== "" ? (
            <div className="space-y-3">
              <div className="flex items-center justify-between text-xs font-medium text-emerald-600 bg-emerald-50 p-3 rounded-lg border border-emerald-100">
                <span className="flex items-center gap-1.5">✓ Documento de propuesta cargado correctamente</span>
                <div className="flex items-center gap-3">
                  <a href={licitacion.licitacion_documento_url} target="_blank" rel="noreferrer" className="underline hover:text-emerald-700 font-semibold">
                    Ver actual
                  </a>
                  {mostrarFormularioEdicion && !isConfirmingDoc && (
                    <button type="button" onClick={() => setIsConfirmingDoc(true)} className="text-rose-600 hover:text-rose-800 font-semibold underline">
                      Cambiar
                    </button>
                  )}
                </div>
              </div>

              {isConfirmingDoc && (
                <div className="p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs space-y-2">
                  <p className="text-amber-800 font-medium">¿Deseas quitar este documento para subir otro?</p>
                  <div className="flex items-center gap-2">
                    <button
                      type="button"
                      onClick={() => {
                        setIsConfirmingDoc(false);
                        setLicitacion((prev) => ({ ...prev, licitacion_documento_url: null }));
                        mostrarAlerta("Puedes subir un nuevo documento.", "success");
                      }}
                      className="bg-amber-600 hover:bg-amber-700 text-white font-medium px-3 py-1.5 rounded"
                    >
                      Sí, cambiar
                    </button>
                    <button type="button" onClick={() => setIsConfirmingDoc(false)} className="bg-white border border-gray-300 text-ink-700 px-3 py-1.5 rounded">
                      Cancelar
                    </button>
                  </div>
                </div>
              )}
            </div>
          ) : (
            mostrarFormularioEdicion && <UploadDocumento licitacionId={id} onUploaded={loadData} />
          )}
        </div>
      </div>

      <div className="card p-6">
        <h3 className="mb-2 font-display text-base font-semibold text-ink-900">Historial de cambios</h3>
        <HistorialList historial={historial} />
      </div>
    </div>
  );
}