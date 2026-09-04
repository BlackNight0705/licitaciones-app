const ESTADO_STYLES = {
  borrador: "bg-ink-100 text-ink-700",
  abierta: "bg-brand-100 text-brand-800",
  en_evaluacion: "bg-amber-100 text-amber-800",
  adjudicada: "bg-emerald-100 text-emerald-800",
  ganada: "bg-emerald-100 text-emerald-800",
  cerrada: "bg-ink-100 text-ink-500",
  perdida: "bg-rose-100 text-rose-700",
  cancelada: "bg-rose-100 text-rose-700",
  // Estados financieros opcionales por si los quieres mostrar como badges independientes
  pagada: "bg-emerald-100 text-emerald-800 border border-emerald-300",
  pago_parcial: "bg-blue-100 text-blue-800",
  pendiente_pago: "bg-amber-100 text-amber-800",
};

const ESTADO_LABELS = {
  borrador: "Borrador",
  abierta: "Abierta",
  en_evaluacion: "En evaluación",
  adjudicada: "Adjudicada",
  ganada: "Ganada",
  cerrada: "Cerrada",
  perdida: "Perdida",
  cancelada: "Cancelada",
  pagada: "Pagada / Cobrada",
  pago_parcial: "Pago Parcial",
  pendiente_pago: "Pendiente de Pago",
};

export default function Badge({ estado, tipo = "licitacion" }) {
  const key = (estado || "").toLowerCase().replace(/\s+/g, "_");
  const style = ESTADO_STYLES[key] || "bg-brand-100 text-brand-800";
  const label = ESTADO_LABELS[key] || estado || "Sin estado";

  return (
    <span
      className={`inline-flex items-center rounded-full px-2.5 py-1 text-xs font-medium ${style}`}
    >
      {label}
    </span>
  );
}