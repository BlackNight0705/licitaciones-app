import { useState, useEffect } from "react";
import { Loader2 } from "lucide-react";
import Modal from "../ui/Modal.jsx";
import { createLicitacion } from "../../api/licitaciones.js";
import { getClientes } from "../../api/cliente.js";

const initialForm = {
  titulo: "",
  descripcion: "",
  entidad: "",
  cliente_id: "",
  presupuesto: "",
  fecha_cierre: "",
};

export default function LicitacionForm({ isOpen, onClose, onCreated }) {
  const [form, setForm] = useState(initialForm);
  const [clientes, setClientes] = useState([]);
  const [isLoadingClientes, setIsLoadingClientes] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (isOpen) {
      loadClientes();
    }
  }, [isOpen]);

  const loadClientes = async () => {
    setIsLoadingClientes(true);
    try {
      const data = await getClientes();
      setClientes(Array.isArray(data) ? data : data?.items || []);
    } catch (err) {
      console.error("No se pudieron cargar los clientes", err);
    } finally {
      setIsLoadingClientes(false);
    }
  };

  const handleChange = (field) => (e) =>
    setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const handleClose = () => {
    setForm(initialForm);
    setError(null);
    onClose();
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      const payload = {
        licitacion_titulo: form.titulo,
        licitacion_descripcion: form.descripcion,
        licitacion_presupuesto_maximo: form.presupuesto ? Number(form.presupuesto) : 0,
        licitacion_fecha_limite: form.fecha_cierre ? `${form.fecha_cierre}T00:00:00` : null,
        licitacion_estado: "borrador",
        licitacion_cliente_id: form.cliente_id ? Number(form.cliente_id) : 1,
        // Si tu backend requiere explícitamente el usuario_id en el payload o lo saca del token:
        // licitacion_usuario_id: 1, 
      };
      const nueva = await createLicitacion(payload);
      onCreated?.(nueva);
      handleClose();
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (Array.isArray(detail)) {
        setError(detail.map(d => `${d.loc.join('.')}: ${d.msg}`).join(', '));
      } else {
        setError(detail || "No se pudo crear la licitación.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Nueva licitación">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="rounded-lg bg-rose-50 px-3.5 py-2.5 text-sm text-rose-700">
            {error}
          </div>
        )}

        <div>
          <label className="label-field">Título</label>
          <input
            required
            value={form.titulo}
            onChange={handleChange("titulo")}
            className="input-field"
            placeholder="Suministro de equipos informáticos"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label-field">Entidad convocante (Texto)</label>
            <input
              required
              value={form.entidad}
              onChange={handleChange("entidad")}
              className="input-field"
              placeholder="Ministerio de..."
            />
          </div>
          <div>
            <label className="label-field">Cliente Asociado</label>
            <select
              value={form.cliente_id}
              onChange={handleChange("cliente_id")}
              className="input-field"
            >
              <option value="">Selecciona un cliente...</option>
              {clientes.map((c) => (
                <option key={c.id ?? c.cliente_id} value={c.id ?? c.cliente_id}>
                  {c.nombre ?? c.cliente_nombre}
                </option>
              ))}
            </select>
          </div>
        </div>

        <div>
          <label className="label-field">Descripción</label>
          <textarea
            value={form.descripcion}
            onChange={handleChange("descripcion")}
            rows={3}
            className="input-field resize-none"
            placeholder="Detalle del objeto de la licitación"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label-field">Presupuesto</label>
            <input
              type="number"
              min="0"
              step="0.01"
              value={form.presupuesto}
              onChange={handleChange("presupuesto")}
              className="input-field"
              placeholder="0.00"
            />
          </div>
          <div>
            <label className="label-field">Fecha de cierre</label>
            <input
              type="date"
              value={form.fecha_cierre}
              onChange={handleChange("fecha_cierre")}
              className="input-field"
            />
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-2">
          <button type="button" onClick={handleClose} className="btn-secondary">
            Cancelar
          </button>
          <button type="submit" disabled={isSubmitting} className="btn-primary">
            {isSubmitting && <Loader2 size={16} className="animate-spin" />}
            {isSubmitting ? "Creando..." : "Crear licitación"}
          </button>
        </div>
      </form>
    </Modal>
  );
}