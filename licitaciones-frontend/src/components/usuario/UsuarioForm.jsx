import { useState } from "react";
import { Loader2 } from "lucide-react";
import Modal from "../ui/Modal.jsx";
import { createUsuario } from "../../api/usuario.js";

const initialForm = {
  usuario_nombre: "",
  usuario_email: "",
  usuario_password: "",
  usuario_rol: "usuario", // 'usuario' o 'admin'
};

export default function UsuarioForm({ isOpen, onClose, onCreated }) {
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
      const nuevoUsuario = await createUsuario(form);
      onCreated?.(nuevoUsuario);
      handleClose();
    } catch (err) {
      const detail = err.response?.data?.detail;
      if (typeof detail === 'string') {
        setError(detail);
      } else {
        setError("No se pudo crear el usuario.");
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Registrar nuevo usuario">
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && (
          <div className="rounded-lg bg-rose-50 px-3.5 py-2.5 text-sm text-rose-700">
            {error}
          </div>
        )}

        <div>
          <label className="label-field">Nombre</label>
          <input
            required
            value={form.usuario_nombre}
            onChange={handleChange("usuario_nombre")}
            className="input-field"
            placeholder="Nombre completo"
          />
        </div>

        <div>
          <label className="label-field">Correo electrónico</label>
          <input
            type="email"
            required
            value={form.usuario_email}
            onChange={handleChange("usuario_email")}
            className="input-field"
            placeholder="correo@ejemplo.com"
          />
        </div>

        <div>
          <label className="label-field">Contraseña temporal</label>
          <input
            type="password"
            required
            value={form.usuario_password}
            onChange={handleChange("usuario_password")}
            className="input-field"
            placeholder="••••••••"
          />
        </div>

        <div>
          <label className="label-field">Rol del sistema</label>
          <select
            value={form.usuario_rol}
            onChange={handleChange("usuario_rol")}
            className="input-field"
          >
            <option value="usuario">Usuario Estándar</option>
            <option value="admin">Administrador</option>
          </select>
        </div>

        <div className="flex justify-end gap-3 pt-2">
          <button type="button" onClick={handleClose} className="btn-secondary">
            Cancelar
          </button>
          <button type="submit" disabled={isSubmitting} className="btn-primary">
            {isSubmitting && <Loader2 size={16} className="animate-spin" />}
            {isSubmitting ? "Registrando..." : "Crear usuario"}
          </button>
        </div>
      </form>
    </Modal>
  );
}