import { X } from "lucide-react";

export default function Modal({ isOpen, onClose, title, children, widthClass = "max-w-lg" }) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div
        className="absolute inset-0 bg-ink-900/40 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden="true"
      />
      <div
        className={`relative w-full ${widthClass} card max-h-[90vh] overflow-y-auto p-6`}
        role="dialog"
        aria-modal="true"
        aria-label={title}
      >
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-lg font-semibold text-ink-900">{title}</h2>
          <button
            type="button"
            onClick={onClose}
            className="rounded-lg p-1.5 text-ink-400 transition-colors hover:bg-brand-50 hover:text-ink-700"
            aria-label="Cerrar"
          >
            <X size={20} />
          </button>
        </div>
        {children}
      </div>
    </div>
  );
}
