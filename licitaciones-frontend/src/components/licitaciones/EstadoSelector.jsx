import { useState } from "react";
import { Loader2 } from "lucide-react";
import { cambiarEstadoLicitacion } from "../../api/licitaciones.js";

const ESTADOS = [
  { value: "borrador", label: "Borrador" },
  { value: "abierta", label: "Abierta" },
  { value: "en_evaluacion", label: "En evaluación" },
  { value: "adjudicada", label: "Adjudicada" },
  { value: "cerrada", label: "Cerrada" },
  { value: "cancelada", label: "Cancelada" },
];

export default function EstadoSelector({ licitacionId, estadoActual, onUpdated }) {
  const [isUpdating, setIsUpdating] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = async (e) => {
    const nuevoEstado = e.target.value;
    if (!nuevoEstado || nuevoEstado === estadoActual) return;

    setIsUpdating(true);
    setError(null);
    try {
      const actualizada = await cambiarEstadoLicitacion(licitacionId, nuevoEstado);
      onUpdated?.(actualizada?.estado ? actualizada : { estado: nuevoEstado });
    } catch (err) {
      setError(
        err.response?.data?.detail || "No se pudo actualizar el estado."
      );
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div>
      <div className="flex items-center gap-2">
        <select
          value={estadoActual || ""}
          onChange={handleChange}
          disabled={isUpdating}
          className="input-field w-auto bg-white text-sm"
        >
          {ESTADOS.map((estado) => (
            <option key={estado.value} value={estado.value}>
              {estado.label}
            </option>
          ))}
        </select>
        {isUpdating && <Loader2 size={16} className="animate-spin text-brand-600" />}
      </div>
      {error && <p className="mt-1.5 text-xs text-rose-600">{error}</p>}
    </div>
  );
}
