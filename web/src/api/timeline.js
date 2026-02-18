import { API_MODE } from "./config";
import { api } from "./client";
import { mockTimeline } from "./mock";

export async function getTimeline(cameraId) {
  if (API_MODE === "mock") return mockTimeline(cameraId);
  const r = await api.get(`/timeline/${cameraId}`);
  return r.data;
}
