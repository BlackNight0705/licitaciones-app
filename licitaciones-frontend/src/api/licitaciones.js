import axiosClient from "./axiosClient";

// --- Licitaciones ---

export const getLicitaciones = (params = {}) =>
  axiosClient.get("/licitaciones/", { params }).then((r) => r.data);

export const getLicitacion = (id) =>
  axiosClient.get(`/licitaciones/${id}`).then((r) => r.data);

export const createLicitacion = (payload) =>
  axiosClient.post("/licitaciones/", payload).then((r) => r.data);

export const actualizarLicitacion = (id, payload) =>
  axiosClient.put(`/licitaciones/${id}`, payload).then((r) => r.data);

export const cambiarEstadoLicitacion = (id, nuevoEstado) =>
  axiosClient
    .post(`/licitaciones/${id}/estado/${encodeURIComponent(nuevoEstado)}`)
    .then((r) => r.data);

export const eliminarLicitacion = (id) =>
  axiosClient.delete(`/licitaciones/${id}`).then((r) => r.data);

// --- Productos ---

export const agregarProducto = (licitacionId, producto) =>
  axiosClient
    .post(`/licitaciones/${licitacionId}/productos`, producto)
    .then((r) => r.data);

export const eliminarProducto = (licitacionId, productoId) =>
  axiosClient
    .delete(`/licitaciones/${licitacionId}/productos/${productoId}`)
    .then((r) => r.data);

// --- Documentos ---

export const subirArchivo = (file, onUploadProgress) => {
  const formData = new FormData();
  formData.append("file", file);
  return axiosClient
    .post("/upload/", formData, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress,
    })
    .then((r) => r.data);
};

export const vincularDocumento = (licitacionId, file, onUploadProgress) => {
  const formData = new FormData();
  formData.append("archivo", file);
  
  return axiosClient
    .post(`/licitaciones/${licitacionId}/documento`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
      onUploadProgress,
    })
    .then((r) => r.data);
};

// --- Historial ---

export const getHistorial = (licitacionId) =>
  axiosClient
    .get(`/licitaciones/${licitacionId}/historial`)
    .then((r) => r.data);

// --- Usuarios ---

export const getUsuarios = () =>
  axiosClient.get("/usuarios/").then((r) => r.data);

export const createUsuario = (userData) =>
  axiosClient.post("/usuarios/", userData).then((r) => r.data);

// --- Clientes ---

export const getClientes = () =>
  axiosClient.get("/cliente/").then((r) => r.data);

export const createCliente = (clienteData) =>
  axiosClient.post("/cliente/", clienteData).then((r) => r.data);