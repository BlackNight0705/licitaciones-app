const ESTADO_STYLES = {
  borrador: "bg-ink-100 text-ink-700",
  abierta: "bg-brand-100 text-brand-800",
  en_evaluacion: "bg-amber-100 text-amber-800",
  adjudicada: "bg-emerald-100 text-emerald-800",
  cerrada: "bg-ink-100 text-ink-500",
  cancelada: "bg-rose-100 text-rose-700",
};

const ESTADO_LABELS = {
  borrador: "Borrador",
  abierta: "Abierta",
  en_evaluacion: "En evaluación",
  adjudicada: "Adjudicada",
  cerrada: "Cerrada",
  cancelada: "Cancelada",
};

export default function Badge({ estado }) {
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
