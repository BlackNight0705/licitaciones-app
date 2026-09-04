import { useState } from "react";
import { Trash2, Loader2, Package, AlertTriangle, CheckCircle2 } from "lucide-react";
import { eliminarProducto } from "../../api/licitaciones.js";

export default function ProductoList({ licitacionId, productos, presupuestoMaximo, onRemoved, readOnly = false }) {
  const [deletingId, setDeletingId] = useState(null);

  const handleDelete = async (productoId) => {
    setDeletingId(productoId);
    try {
      await eliminarProducto(licitacionId, productoId);
      onRemoved?.(productoId);
    } catch (err) {
      console.error(err);
    } finally {
      setDeletingId(null);
    }
  };

  const formatCurrency = (value) =>
    new Intl.NumberFormat("es-ES", {
      style: "currency",
      currency: "USD",
    }).format(value || 0);

  // Calcular el subtotal/total acumulado de todos los productos
  const costoTotal = (productos || []).reduce((acc, item) => {
    const cantidad = item.cantidad ?? item.licitacion_producto_cantidad ?? 0;
    const precio = item.precio_unitario ?? item.licitacion_producto_precio_unitario ?? item.producto?.precio_unitario ?? item.producto?.producto_precio_unitario ?? 0;
    return acc + (cantidad * precio);
  }, 0);

  const sePasaDelPresupuesto = presupuestoMaximo != null && costoTotal > presupuestoMaximo;

  if (!productos || productos.length === 0) {
    return (
      <div className="space-y-4">
        <div className="flex items-center gap-2 py-6 text-sm text-ink-500">
          <Package size={16} />
          Aún no se han agregado productos.
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Listado de productos */}
      <div className="divide-y divide-brand-100">
        {productos.map((item) => {
          const productoKey = item.id || item.licitacion_producto_id;
          const nombreProducto = item.nombre || item.producto_nombre || item.producto?.nombre || item.producto?.producto_nombre || "Producto sin nombre";
          const cantidadItem = item.cantidad ?? item.licitacion_producto_cantidad ?? 0;
          const precioItem = item.precio_unitario ?? item.licitacion_producto_precio_unitario ?? item.producto?.precio_unitario ?? item.producto?.producto_precio_unitario ?? 0;
          const subtotalItem = cantidadItem * precioItem;

          return (
            <div key={productoKey} className="flex items-center justify-between py-3">
              <div>
                <p className="font-medium text-ink-900">{nombreProducto}</p>
                <p className="text-sm text-ink-500">
                  {cantidadItem} unidad{cantidadItem !== 1 && "es"} · {formatCurrency(precioItem)} c/u
                  <span className="font-semibold text-ink-700 ml-2">({formatCurrency(subtotalItem)})</span>
                </p>
              </div>
              {!readOnly && (
                <button
                  type="button"
                  onClick={() => handleDelete(productoKey)}
                  disabled={deletingId === productoKey}
                  className="rounded-lg p-2 text-ink-400 transition-colors hover:bg-rose-50 hover:text-rose-600"
                  aria-label={`Eliminar ${nombreProducto}`}
                >
                  {deletingId === productoKey ? (
                    <Loader2 size={16} className="animate-spin" />
                  ) : (
                    <Trash2 size={16} />
                  )}
                </button>
              )}
            </div>
          );
        })}
      </div>

      {/* Resumen de Total vs Presupuesto */}
      <div className={`p-4 rounded-xl border flex flex-wrap items-center justify-between gap-2 ${
        sePasaDelPresupuesto 
          ? "bg-rose-50 border-rose-200 text-rose-900" 
          : "bg-emerald-50 border-emerald-200 text-emerald-900"
      }`}>
        <div className="flex items-center gap-2">
          {sePasaDelPresupuesto ? (
            <AlertTriangle size={20} className="text-rose-600 shrink-0" />
          ) : (
            <CheckCircle2 size={20} className="text-emerald-600 shrink-0" />
          )}
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider opacity-80">Costo Total de Productos</p>
            <p className="text-lg font-bold">{formatCurrency(costoTotal)}</p>
          </div>
        </div>

        {presupuestoMaximo != null && (
          <div className="text-right">
            <p className="text-xs font-medium opacity-80">Presupuesto Máximo: {formatCurrency(presupuestoMaximo)}</p>
            {sePasaDelPresupuesto ? (
              <p className="text-xs font-bold text-rose-700">¡Supera el presupuesto establecido!</p>
            ) : (
              <p className="text-xs font-medium text-emerald-700">Dentro del presupuesto</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}