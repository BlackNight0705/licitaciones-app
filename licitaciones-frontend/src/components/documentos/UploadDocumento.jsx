import { useRef, useState } from "react";
import { UploadCloud, FileText, X, Eye, Loader2, AlertCircle, CheckCircle2 } from "lucide-react";
import { vincularDocumento } from "../../api/licitaciones.js";

export default function UploadDocumento({ licitacionId, onUploaded }) {
  const [isDragging, setIsDragging] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState(null);
  const inputRef = useRef(null);

  const handleFileSelect = (file) => {
    if (!file) return;
    setError(null);
    setSelectedFile(file);

    // Creamos una URL local temporal para previsualizar el archivo en el navegador
    const objectUrl = URL.createObjectURL(file);
    setPreviewUrl(objectUrl);
  };

  const handleDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files?.[0];
    handleFileSelect(file);
  };

  const handleRemoveFile = () => {
    if (previewUrl) {
      URL.revokeObjectURL(previewUrl); // Liberamos memoria del navegador
    }
    setSelectedFile(null);
    setPreviewUrl(null);
    setProgress(0);
    setError(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  const handleOpenPreview = () => {
    if (previewUrl) {
      window.open(previewUrl, "_blank"); // Abre el archivo en una pestaña nueva para verlo completo
    }
  };

  const handleConfirmUpload = async () => {
    if (!selectedFile) return;
    setIsUploading(true);
    setProgress(0);
    setError(null);

    try {
      const documento = await vincularDocumento(licitacionId, selectedFile, (evt) => {
        if (evt.total) {
          setProgress(Math.round((evt.loaded * 100) / evt.total));
        }
      });

      onUploaded?.(documento);
      handleRemoveFile(); // Limpiamos todo tras el éxito
    } catch (err) {
      setError(err.response?.data?.detail || "No se pudo subir el documento.");
    } finally {
      setIsUploading(false);
    }
  };

  return (
    <div className="w-full">
      {!selectedFile ? (
        <div
          onDragOver={(e) => {
            e.preventDefault();
            setIsDragging(true);
          }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          onClick={() => inputRef.current?.click()}
          className={`flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border-2 border-dashed
            px-6 py-8 text-center transition-colors
            ${isDragging ? "border-brand-500 bg-brand-50" : "border-brand-200 bg-white hover:bg-brand-50/50"}`}
        >
          <input
            ref={inputRef}
            type="file"
            className="hidden"
            onChange={(e) => handleFileSelect(e.target.files?.[0])}
          />
          <UploadCloud size={28} className="text-brand-500" />
          <p className="text-sm text-ink-600">
            <span className="font-medium text-brand-700">Haz clic para seleccionar</span> o arrastra un archivo
          </p>
          <p className="text-xs text-ink-400">PDF, Word, Excel o imágenes</p>
        </div>
      ) : (
        <div className="rounded-xl border border-brand-200 bg-brand-50/30 p-4">
          <div className="flex items-center justify-between gap-3">
            
            {/* Al hacer clic en el contenedor del archivo o en el icono de ver, se abre la vista previa */}
            <div 
              onClick={handleOpenPreview}
              className="flex items-center gap-3 overflow-hidden cursor-pointer group flex-1"
              title="Haz clic para ver el documento"
            >
              <div className="rounded-lg bg-brand-100 p-2 text-brand-600 group-hover:bg-brand-200 transition-colors">
                <FileText size={22} />
              </div>
              <div className="overflow-hidden">
                <p className="truncate text-sm font-medium text-ink-800 group-hover:underline">
                  {selectedFile.name}
                </p>
                <p className="text-xs text-ink-400 flex items-center gap-1">
                  {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB • <span className="text-brand-600 inline-flex items-center gap-0.5"><Eye size={12}/> Ver documento</span>
                </p>
              </div>
            </div>

            {/* Botón para eliminar/cambiar de archivo */}
            {!isUploading && (
              <button
                type="button"
                onClick={handleRemoveFile}
                className="rounded-lg p-1.5 text-ink-400 hover:bg-rose-50 hover:text-rose-600 transition-colors"
                title="Eliminar archivo"
              >
                <X size={18} />
              </button>
            )}
          </div>

          {/* Barra de progreso */}
          {isUploading && (
            <div className="mt-3">
              <div className="flex justify-between text-xs text-ink-600 mb-1">
                <span>Subiendo a Supabase...</span>
                <span>{progress}%</span>
              </div>
              <div className="h-2 w-full rounded-full bg-brand-100 overflow-hidden">
                <div 
                  className="h-full bg-brand-600 transition-all duration-300" 
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>
          )}

          {/* Botones de acción */}
          {!isUploading && (
            <div className="mt-4 flex justify-end gap-2">
              <button
                type="button"
                onClick={handleRemoveFile}
                className="rounded-lg px-3 py-1.5 text-xs font-medium text-ink-600 hover:bg-ink-100 transition-colors"
              >
                Cancelar
              </button>
              <button
                type="button"
                onClick={handleConfirmUpload}
                className="inline-flex items-center gap-1.5 rounded-lg bg-brand-600 px-4 py-1.5 text-xs font-medium text-white hover:bg-brand-700 transition-colors shadow-sm"
              >
                <CheckCircle2 size={14} />
                Guardar y Subir
              </button>
            </div>
          )}
        </div>
      )}

      {error && (
        <div className="mt-3 flex items-center gap-2 text-sm text-rose-600">
          <AlertCircle size={16} />
          {error}
        </div>
      )}
    </div>
  );
}