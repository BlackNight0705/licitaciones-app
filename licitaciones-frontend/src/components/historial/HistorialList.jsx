import { History } from "lucide-react";

export default function HistorialList({ historial }) {
  if (!historial || historial.length === 0) {
    return (
      <div className="flex items-center gap-2 py-6 text-sm text-ink-500">
        <History size={16} />
        Sin movimientos registrados todavía.
      </div>
    );
  }

  return (
    <ol className="relative ml-2.5 space-y-5 border-l border-brand-200 pl-6">
      {historial.map((evento, idx) => (
        <li key={evento.historial_transicion_id ?? idx} className="relative">
          <span className="absolute -left-[1.71rem] top-1 h-3 w-3 rounded-full border-2 border-white bg-brand-500" />
          <p className="text-sm font-medium text-ink-900 capitalize">
            {evento.historial_transicion_estado_anterior && evento.historial_transicion_estado_nuevo
              ? `Cambio de estado: ${evento.historial_transicion_estado_anterior} ➔ ${evento.historial_transicion_estado_nuevo}`
              : "Actualización"}
          </p>
          <p className="text-xs text-ink-400">
            {evento.historial_transicion_fecha_transicion
              ? new Date(evento.historial_transicion_fecha_transicion).toLocaleString("es-ES")
              : "Fecha no disponible"}
          </p>
        </li>
      ))}
    </ol>
  );
}