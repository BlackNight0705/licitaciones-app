import React, { useState } from 'react';
import { DollarSign, AlertCircle, CreditCard } from 'lucide-react';
import api from '../../api/axiosClient'; 

const SeccionPagosModal = ({ licitacion, onPagoExitoso, readOnly = false }) => {
  const [modalAbierto, setModalAbierto] = useState(false);
  const [monto, setMonto] = useState('');
  const [metodoPago, setMetodoPago] = useState('transferencia');
  const [error, setError] = useState('');
  const [cargando, setCargando] = useState(false);

  if (!licitacion) return null;

  // 1. Extraer presupuesto
  const presupuestoTotal = Number(
    licitacion.licitacion_presupuesto_maximo || 
    licitacion.presupuesto_maximo || 
    licitacion.presupuesto || 
    0
  );

  // 2. Extraer pagos
  const pagosRegistrados = Array.isArray(licitacion.pagos) ? licitacion.pagos : [];
  const totalPagado = pagosRegistrados.reduce((acc, p) => acc + (Number(p.pago_monto || p.monto) || 0), 0);
  
  const saldoPendiente = Math.max(0, presupuestoTotal - totalPagado);

  // 3. Revisar el estado de forma amplia
  const estadoTexto = String(
    licitacion.licitacion_estado || 
    licitacion.estado || 
    licitacion.status || 
    ''
  ).toLowerCase();

  const esCobradaExplicita = Boolean(licitacion.cobrada || licitacion.is_cobrada) || estadoTexto.includes('cobrad');
  const estaPagadaTotalmente = saldoPendiente === 0 || esCobradaExplicita;

  // AJUSTE DE ESTADOS: Permitir en borrador o activa, bloquear solo en terminales negativos reales
  const estadosBloqueadosAbsolutos = ["perdida", "finalizada", "cancelada"];
  const estadoBloqueado = estadosBloqueadosAbsolutos.some(e => estadoTexto.includes(e));

  const puedeRealizarPago = !readOnly && !estadoBloqueado && saldoPendiente > 0;

  // 4. Validaciones numéricas estrictas contra negativos
  const montoNum = parseFloat(monto) || 0;
  const esNegativo = monto !== '' && montoNum < 0;
  const totalProyectadoPagos = totalPagado + montoNum;
  const superaPresupuesto = presupuestoTotal > 0 && totalProyectadoPagos > presupuestoTotal;

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (readOnly) return;
    setError('');

    if (esNegativo || montoNum <= 0) {
      setError('No se permiten montos negativos o iguales a cero.');
      return;
    }

    if (montoNum > saldoPendiente) {
      setError(`El pago no puede superar el saldo pendiente ($${saldoPendiente.toFixed(2)}).`);
      return;
    }

    if (superaPresupuesto) {
      setError(`El abono excede el presupuesto máximo permitido ($${presupuestoTotal.toFixed(2)}).`);
      return;
    }

    try {
      setCargando(true);
      await api.post('/pagos/', {
        pago_licitacion_id: licitacion.licitacion_id || licitacion.id,
        pago_monto: montoNum,
        pago_metodo_pago: metodoPago
      });

      setMonto('');
      setModalAbierto(false);
      if (onPagoExitoso) onPagoExitoso();
    } catch (err) {
      const detalle = err.response?.data?.detail;
      let mensajeError = 'Error al procesar el pago.';

      if (typeof detalle === 'string') {
        mensajeError = detalle;
      } else if (Array.isArray(detalle)) {
        mensajeError = detalle.map(d => `${d.loc.join('.')}: ${d.msg}`).join(' | ');
      } else {
        mensajeError = JSON.stringify(detalle);
      }

      setError(mensajeError);
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="card p-6 mt-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900 flex items-center gap-2">
          <DollarSign className="w-5 h-5 text-indigo-600" />
          Control Financiero y Pagos
        </h3>
        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
          estaPagadaTotalmente ? 'bg-emerald-100 text-emerald-800' : 'bg-amber-100 text-amber-800'
        }`}>
          {estaPagadaTotalmente ? 'Pagada / Cobrada' : 'Pendiente de Pago'}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6 bg-gray-50 p-4 rounded-md">
        <div>
          <p className="text-sm text-gray-500">Presupuesto Total</p>
          <p className="text-xl font-bold text-gray-800">${presupuestoTotal.toFixed(2)}</p>
        </div>
        <div>
          <p className="text-sm text-gray-500">Saldo Pendiente (Restante)</p>
          <p className="text-xl font-bold text-indigo-600">${saldoPendiente.toFixed(2)}</p>
        </div>
      </div>

      {puedeRealizarPago ? (
        <button
          onClick={() => setModalAbierto(true)}
          className="inline-flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 transition"
        >
          <CreditCard className="w-4 h-4" />
          Registrar Nuevo Pago (Abono)
        </button>
      ) : (
        <div className="p-3 rounded-lg text-sm flex items-center gap-2 bg-emerald-50 border border-emerald-100 text-emerald-800">
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>
            {estaPagadaTotalmente 
              ? "Esta licitación ya se encuentra pagada en su totalidad ($0.00 restante)." 
              : `El registro de pagos no está disponible para este estado.`}
          </span>
        </div>
      )}

      {modalAbierto && !readOnly && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6 relative">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Registrar Abono Parcial</h3>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Monto del Abono (Restante: ${saldoPendiente.toFixed(2)})
                </label>
                <input
                  type="number"
                  step="0.01"
                  min="0.01"
                  max={saldoPendiente}
                  value={monto}
                  onChange={(e) => setMonto(e.target.value)}
                  placeholder="0.00"
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-indigo-500 focus:border-indigo-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Método de Pago</label>
                <select
                  value={metodoPago}
                  onChange={(e) => setMetodoPago(e.target.value)}
                  className="w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-indigo-500 focus:border-indigo-500"
                >
                  <option value="transferencia">Transferencia Bancaria</option>
                  <option value="efectivo">Efectivo</option>
                  <option value="cheque">Cheque</option>
                  <option value="tarjeta">Tarjeta de Crédito / Débito</option>
                </select>
              </div>

              {/* Alerta de números negativos */}
              {esNegativo && (
                <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-md flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>No se permiten números negativos.</span>
                </div>
              )}

              {/* Alerta si supera presupuesto */}
              {superaPresupuesto && !esNegativo && (
                <div className="p-3 bg-red-50 border border-red-200 text-red-700 text-sm rounded-md flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>Este abono excede el presupuesto máximo (${presupuestoTotal.toFixed(2)}).</span>
                </div>
              )}

              {error && (
                <div className="p-3 bg-red-50 text-red-700 text-sm rounded-md flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0" />
                  <span>{error}</span>
                </div>
              )}

              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setModalAbierto(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={cargando || superaPresupuesto || esNegativo}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-md text-sm font-medium hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {cargando ? 'Guardando...' : 'Confirmar Abono'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default SeccionPagosModal;