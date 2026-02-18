# rada-ai v1

Frigate-like, edge-first video security platform for schools — built to work **without hardware** using an **Inference Simulator**.
When Jetson + RTSP feeds arrive, only the input/detector plugins change.

## What you get in v1
- Backend: FastAPI + Postgres (events, timeline, cameras, media)
- Simulator: realistic inference simulation (start/ongoing/peak/end events + snapshots)
- Web UI: Frigate-like UX (Live, Review timeline, Event details, System, Config)

## Quick start (local dev)
### 1) Start Postgres
```bash
docker compose up -d
