const now = Date.now();

const cameras = [
  { id: "cam_1", name: "Gate" },
  { id: "cam_2", name: "Yard" },
  { id: "cam_3", name: "Hallway" },
  { id: "cam_4", name: "Parking" },
];

function rand(arr) {
  return arr[Math.floor(Math.random() * arr.length)];
}

export function mockLogin() {
  return Promise.resolve({ access_token: "mock-token" });
}

export function mockCameras() {
  return Promise.resolve(cameras);
}

export function mockEvents(limit = 50) {
  const types = ["intrusion", "loitering", "vandalism"];
  const labels = ["person", "vehicle"];
  const items = Array.from({ length: limit }).map((_, i) => {
    const id = `evt_mock_${i}`;
    const cam = rand(cameras);
    const state = rand(["start", "ongoing", "peak", "end"]);
    const severity = Math.floor(20 + Math.random() * 70);
    const t0 = new Date(now - i * 60_000).toISOString();
    return {
      id,
      camera_id: cam.id,
      event_type: rand(types),
      severity,
      state,
      ts_start: t0,
      ts_peak: t0,
      ts_end: state === "end" ? t0 : null,
      snapshot_url: null,
      meta: { label: rand(labels), confidence: 0.7, bbox: [220, 160, 520, 520], mode: "mock" },
    };
  });
  return Promise.resolve(items);
}

export function mockTimeline(cameraId) {
  return mockEvents(30).then((ev) =>
    ev
      .filter((e) => e.camera_id === cameraId)
      .map((e) => ({ id: e.id, event_type: e.event_type, severity: e.severity, state: e.state, ts_start: e.ts_start, ts_end: e.ts_end }))
  );
}
