# rada-ai v1 backend

FastAPI + Postgres backend for:
- auth (JWT)
- cameras
- events (Frigate-like lifecycle: start/ongoing/peak/end)
- timeline per camera
- serving snapshots via /media

## Run
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# mac/linux: source .venv/bin/activate
pip install -r requirements.txt

# set env vars (or use .env in your shell)
uvicorn app.main:app --reload --port 8000
