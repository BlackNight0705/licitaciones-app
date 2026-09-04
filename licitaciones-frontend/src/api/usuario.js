import api from './axiosClient';

export const createUsuario = async (userData) => {
  const response = await api.post('/usuario/', userData);
  return response.data;
};

export const getUsuarios = async () => {
  const response = await api.get('/usuario/');
  return response.data;
};