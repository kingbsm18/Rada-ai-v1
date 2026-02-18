import { API_MODE } from "./config";
import { api, setToken } from "./client";
import { mockLogin } from "./mock";

export async function login(username, password) {
  if (API_MODE === "mock") {
    const data = await mockLogin();
    setToken(data.access_token);
    return data;
  }
  const form = new URLSearchParams();
  form.append("username", username);
  form.append("password", password);

  const r = await api.post("/auth/login", form, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  setToken(r.data.access_token);
  return r.data;
}
