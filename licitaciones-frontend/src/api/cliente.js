import api from './axiosClient';

export const getClientes = async () => {
  const response = await api.get('/cliente/');
  return response.data;
};

export const createCliente = async (clienteData) => {
  const response = await api.post('/cliente/', clienteData);
  return response.data;
};