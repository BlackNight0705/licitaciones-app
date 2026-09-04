import { useState } from "react";
import { Loader2, Plus } from "lucide-react";
import { agregarProducto } from "../../api/licitaciones.js";

export default function ProductoForm({ licitacionId, onAdded, readOnly = false }) {
  const [form, setForm] = useState({ nombre: "", cantidad: "", precio_unitario: "" });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState(null);

  if (readOnly) {
    return null;
  }

  const handleChange = (field) => (e) =>
    setForm((prev) => ({ ...prev, [field]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setError(null);
    try {
      const payload = {
        nombre: form.nombre,
        cantidad: Number(form.cantidad),
        precio_unitario: Number(form.precio_unitario),
      };
      const nuevoProducto = await agregarProducto(licitacionId, payload);
      onAdded?.(nuevoProducto);
      setForm({ nombre: "", cantidad: "", precio_unitario: "" });
    } catch (err) {
      setError(err.response?.data?.detail || "No se pudo agregar el producto.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-wrap items-end gap-3">
      <div className="min-w-[10rem] flex-1">
        <label className="label-field">Producto</label>
        <input
          required
          value={form.nombre}
          onChange={handleChange("nombre")}
          className="input-field"
          placeholder="Laptop 14''"
        />
      </div>
      <div className="w-24">
        <label className="label-field">Cantidad</label>
        <input
          required
          type="number"
          min="1"
          value={form.cantidad}
          onChange={handleChange("cantidad")}
          className="input-field"
        />
      </div>
      <div className="w-32">
        <label className="label-field">Precio unit.</label>
        <input
          required
          type="number"
          min="0"
          step="0.01"
          value={form.precio_unitario}
          onChange={handleChange("precio_unitario")}
          className="input-field"
        />
      </div>
      <button type="submit" disabled={isSubmitting} className="btn-primary h-[42px]">
        {isSubmitting ? <Loader2 size={16} className="animate-spin" /> : <Plus size={16} />}
        Agregar
      </button>
      {error && <p className="w-full text-xs text-rose-600">{error}</p>}
    </form>
  );
}