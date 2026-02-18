import { API_MODE } from "./config";
import { api } from "./client";
import { mockCameras } from "./mock";

export async function getCameras() {
  if (API_MODE === "mock") return mockCameras();
  const r = await api.get("/cameras");
  return r.data;
}
