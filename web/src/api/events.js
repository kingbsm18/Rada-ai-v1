import { API_MODE } from "./config";
import { api } from "./client";
import { mockEvents } from "./mock";

export async function getEvents(limit = 200) {
  if (API_MODE === "mock") return mockEvents(60);
  const r = await api.get("/events", { params: { limit } });
  return r.data;
}
