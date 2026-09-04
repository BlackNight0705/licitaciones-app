import { useState } from "react";
import { Loader2 } from "lucide-react";
import Modal from "../ui/Modal.jsx";
import { createCliente } from "../../api/cliente.js";

const initialForm = {
  cliente_nombre: "",
  cliente_email: "",
  cliente_telefono: "",
  cliente_empresa: "",
};

export default function ClienteForm({ isOpen, onClose, onCreated }) {
  const [form, setForm] = useState(initialForm);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

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
      const nuevoCliente = await createCliente(form);
      onCreated?.(nuevoCliente);
      handleClose();
    } catch (err) {
      setError(err.response?.data?.detail || "No se pudo registrar el cliente.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Registrar nuevo cliente">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="rounded-lg bg-rose-50 px-3.5 py-2.5 text-sm text-rose-700">
            {error}
          </div>
        )}

        <div>
          <label className="label-field">Nombre del Cliente</label>
          <input
            required
            value={form.cliente_nombre}
            onChange={handleChange("cliente_nombre")}
            className="input-field"
            placeholder="Nombre completo"
          />
        </div>

        <div>
          <label className="label-field">Correo electrónico (para notificaciones)</label>
          <input
            type="email"
            required
            value={form.cliente_email}
            onChange={handleChange("cliente_email")}
            className="input-field"
            placeholder="correo@ejemplo.com"
          />
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="label-field">Empresa (Opcional)</label>
            <input
              value={form.cliente_empresa}
              onChange={handleChange("cliente_empresa")}
              className="input-field"
              placeholder="Nombre de la empresa"
            />
          </div>
          <div>
            <label className="label-field">Teléfono (Opcional)</label>
            <input
              value={form.cliente_telefono}
              onChange={handleChange("cliente_telefono")}
              className="input-field"
              placeholder="Teléfono de contacto"
            />
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-2">
          <button type="button" onClick={handleClose} className="btn-secondary">
            Cancelar
          </button>
          <button type="submit" disabled={isSubmitting} className="btn-primary">
            {isSubmitting && <Loader2 size={16} className="animate-spin" />}
            {isSubmitting ? "Guardando..." : "Guardar cliente"}
          </button>
        </div>
      </form>
    </Modal>
  );
}