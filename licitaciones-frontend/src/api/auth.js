import axiosClient from "./axiosClient";

/**
 * FastAPI con OAuth2PasswordRequestForm espera un body
 * application/x-www-form-urlencoded con los campos `username` y `password`,
 * no JSON. Por eso se construye un URLSearchParams en vez de un objeto plano.
 */
export async function login(username, password) {
  const body = new URLSearchParams();
  body.append("username", username);
  body.append("password", password);

  const { data } = await axiosClient.post("/login", body, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });

  // Se espera una respuesta tipo { access_token, token_type }
  return data;
}
