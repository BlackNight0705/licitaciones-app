import React, { useState } from 'react';
import { DollarSign, AlertCircle, CreditCard, CheckCircle2 } from 'lucide-react';
import api from '../api/axios';

const SeccionPagosModal = ({ licitacion, onPagoExitoso }) => {
  const [modalAbierto, setModalAbierto] = useState(false);
  const [monto, setMonto] = useState('');
  const [metodoPago, setMetodoPago] = useState('transferencia');
  const [error, setError] = useState('');
  const [cargando, setCargando] = useState(false);

  const pagosRegistrados = licitacion.pagos || [];
  const totalPagado = pagosRegistrados.reduce((acc, p) => acc + p.pago_monto, 0);
  const presupuestoMaximo = licitacion.licitacion_presupuesto_maximo || 0;
  const saldoPendiente = presupuestoMaximo - totalPagado;

  // Estados que prohíben totalmente los pagos (si se perdió o canceló)
  const estadosBloqueadosParaPagos = ["perdida", "finalizada", "cancelada"];
  const puedeRealizarPago = !estadosBloqueadosParaPagos.includes(licitacion.licitacion_estado);

  // Determinamos el texto y color del badge financiero dinámicamente
  const obtenerEstadoFinanciero = () => {
    if (totalPagado >= presupuestoMaximo && presupuestoMaximo > 0) {
      return { texto: 'Pagada / Cobrada', clase: 'bg-emerald-100 text-emerald-800' };
    }
    if (totalPagado > 0) {
      return { texto: 'Pago Parcial', clase: 'bg-blue-100 text-blue-800' };
    }
    return { texto: 'Pendiente de Pago', clase: 'bg-amber-100 text-amber-800' };
  };

  const estadoFinanciero = obtenerEstadoFinanciero();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const montoNum = parseFloat(monto);
    if (!montoNum || montoNum <= 0) {
      setError('Ingresa un monto válido.');
      return;
    }

    if (montoNum > saldoPendiente) {
      setError(`El pago no puede superar el saldo pendiente ($${saldoPendiente.toFixed(2)}).`);
      return;
    }

    try {
      setCargando(true);
      await api.post('/pagos/', {
        pago_licitacion_id: licitacion.licitacion_id || licitacion.id,
        pago_monto: montoNum,
        pago_metodo: metodoPago
      });

      setMonto('');
      setModalAbierto(false);
      if (onPagoExitoso) onPagoExitoso();
    } catch (err) {
      setError(err.response?.data?.detail || 'Error al procesar el pago.');
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
        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${estadoFinanciero.clase}`}>
          {estadoFinanciero.texto}
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6 bg-gray-50 p-4 rounded-md">
        <div>
          <p className="text-sm text-gray-500">Presupuesto Máximo</p>
          <p className="text-xl font-bold text-gray-800">${presupuestoMaximo.toFixed(2)}</p>
        </div>
        <div>
          <p className="text-sm text-gray-500">Saldo Pendiente</p>
          <p className="text-xl font-bold text-indigo-600">${saldoPendiente.toFixed(2)}</p>
        </div>
      </div>

      {/* Si el estado general lo permite y aún hay saldo por cobrar */}
      {puedeRealizarPago && saldoPendiente > 0 ? (
        <button
          onClick={() => setModalAbierto(true)}
          className="inline-flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-md text-sm font-medium hover:bg-indigo-700 transition"
        >
          <CreditCard className="w-4 h-4" />
          Registrar Nuevo Pago
        </button>
      ) : (
        <div className={`p-3 rounded-lg text-sm flex items-center gap-2 ${
          !puedeRealizarPago 
            ? "bg-amber-50 border border-amber-200 text-amber-800" 
            : "bg-emerald-50 border border-emerald-100 text-emerald-800"
        }`}>
          <AlertCircle className="w-4 h-4 shrink-0" />
          <span>
            {!puedeRealizarPago 
              ? `No se pueden registrar pagos porque la licitación se encuentra en estado "${licitacion.licitacion_estado}".`
              : "Esta licitación ha sido pagada en su totalidad."}
          </span>
        </div>
      )}

      {/* Modal de Registro de Pago */}
      {modalAbierto && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="bg-white rounded-lg shadow-xl max-w-md w-full p-6 relative">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Registrar Pago</h3>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Monto del Pago</label>
                <input
                  type="number"
                  step="0.01"
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

              {error && (
                <div className="p-3 bg-red-50 text-red-700 text-sm rounded-md flex items-center gap-2">
                  <AlertCircle className="w-4 h-4" />
                  {error}
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
                  disabled={cargando}
                  className="px-4 py-2 bg-indigo-600 text-white rounded-md text-sm font-medium hover:bg-indigo-700 disabled:opacity-50"
                >
                  {cargando ? 'Guardando...' : 'Confirmar Pago'}
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