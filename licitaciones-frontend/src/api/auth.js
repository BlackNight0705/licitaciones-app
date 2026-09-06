import axiosClient from "./axiosClient";

export async function login(username, password) {
  const body = new URLSearchParams();
  body.append("username", username);
  body.append("password", password);

  try {
    const { data } = await axiosClient.post("/login", body, {
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
    });
    return data; // Retorna el token exitoso
  } catch (error) {
    // Si el backend responde con un 401 o 400, lanzamos un error legible
    if (error.response) {
      if (error.response.status === 401) {
        throw new Error("Usuario o contraseña incorrectos.");
      }
      // Si el backend envía un mensaje específico en el detalle
      if (error.response.data && error.response.data.detail) {
        throw new Error(error.response.data.detail);
      }
    }
    throw new Error("No se pudo conectar con el servidor. Inténtalo más tarde.");
  }
}