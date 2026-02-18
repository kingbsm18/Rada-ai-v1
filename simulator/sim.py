import os
import time
import uuid
import random
from datetime import datetime, timezone
from typing import Dict, Any

import yaml
import requests

from snapshot_gen import generate_snapshot
from video_loop import ffprobe_duration_seconds, ffmpeg_snapshot

API = "http://127.0.0.1:8000"
ADMIN_EMAIL = "admin@rada.ai"
ADMIN_PASSWORD = "admin123"

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MEDIA_DIR = os.path.join(ROOT, "media")
SNAP_DIR = os.path.join(MEDIA_DIR, "snapshots")
VID_DIR = os.path.join(MEDIA_DIR, "videos")

os.makedirs(SNAP_DIR, exist_ok=True)
os.makedirs(VID_DIR, exist_ok=True)

def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

def login() -> str:
    r = requests.post(
        f"{API}/auth/login",
        data={"username": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=10
    )
    r.raise_for_status()
    return r.json()["access_token"]

def get_cameras(token: str):
    r = requests.get(
        f"{API}/cameras",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10
    )
    r.raise_for_status()
    return r.json()

def ingest_event(payload: Dict[str, Any]):
    r = requests.post(f"{API}/events/ingest", json=payload, timeout=10)
    r.raise_for_status()

def load_scenario(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def clamp(v: int, lo: int, hi: int) -> int:
    return max(lo, min(hi, v))

def make_sim_snapshot(event_id: str, cam_name: str, label: str, conf: float, bbox, severity: int, state: str):
    snap_file = os.path.join(SNAP_DIR, f"{event_id}.jpg")
    generate_snapshot(
        out_path=snap_file,
        cam_name=cam_name,
        event_id=event_id,
        label=label,
        conf=conf,
        bbox=bbox,
        severity=severity,
        state=state,
    )
    return os.path.join("snapshots", f"{event_id}.jpg")

def make_video_snapshot(event_id: str, video_path: str, t_sec: float):
    snap_file = os.path.join(SNAP_DIR, f"{event_id}.jpg")
    ok = ffmpeg_snapshot(video_path, snap_file, t_sec=t_sec)
    if not ok:
        return None
    return os.path.join("snapshots", f"{event_id}.jpg")

def main():
    token = login()
    cams = get_cameras(token)
    if not cams:
        print("No cameras found. Run POST /dev/seed first.")
        return

    scenario_path = os.getenv(
        "RADA_SCENARIO",
        os.path.join(os.path.dirname(__file__), "scenarios", "school_day.yaml")
    )
    sc = load_scenario(scenario_path)

    mode = os.getenv("RADA_MODE", "SIM_ONLY").upper()
    video_path = os.getenv("RADA_VIDEO", os.path.join(VID_DIR, "cam1.mp4"))

    duration = None
    loop_start = time.time()

    if mode == "VIDEO_LOOP":
        if not os.path.exists(video_path):
            print(f"[VIDEO_LOOP] Video not found: {video_path}")
            print("Put video at media/videos/cam1.mp4 or set RADA_VIDEO to your mp4 path.")
            return

        duration = ffprobe_duration_seconds(video_path)
        if not duration or duration < 1.0:
            print("[VIDEO_LOOP] Could not detect duration with ffprobe; using fallback 60s.")
            duration = 60.0

    print("RADA simulator started")
    print("Mode:", mode)
    print("Scenario:", sc.get("name"), "|", scenario_path)
    print("Cameras:", [c["id"] for c in cams])
    if mode == "VIDEO_LOOP":
        print("Video:", video_path, "| duration:", duration)

    rate_lo, rate_hi = sc["event_rate_sec_range"]
    sev_lo, sev_hi = sc["severity_base_range"]
    steps_lo, steps_hi = sc["steps_range"]
    labels = sc["labels"]
    event_types = sc["event_types"]

    while True:
        cam = random.choice(cams)
        cam_id = cam["id"]
        cam_name = cam["name"]

        event_id = f"evt_{uuid.uuid4().hex[:10]}"
        event_type = random.choice(event_types)
        label = random.choice(labels)
        conf = random.uniform(0.55, 0.95)

        # bbox for SIM_ONLY (still stored in meta for UI overlays)
        x = random.randint(120, 900)
        y = random.randint(140, 520)
        bw = random.randint(140, 260)
        bh = random.randint(220, 360)

        base_sev = random.randint(sev_lo, sev_hi)

        def snapshot_for_state(state: str, severity: int, bbox):
            if mode == "VIDEO_LOOP":
                now = time.time()
                t = (now - loop_start) % float(duration)
                return make_video_snapshot(event_id, video_path, t_sec=t)
            return make_sim_snapshot(event_id, cam_name, label, conf, bbox, severity, state)

        def post_state(state: str, severity: int):
            nonlocal x, y, conf
            snapshot_path = snapshot_for_state(state, severity, (x, y, x + bw, y + bh))

            payload = {
                "event_id": event_id,
                "camera_id": cam_id,
                "event_type": event_type,
                "severity": severity,
                "state": state,
                "ts": iso_now(),
                "snapshot_path": snapshot_path,
                "clip_path": None,
                "meta": {
                    "detector": "sim_video" if mode == "VIDEO_LOOP" else "sim",
                    "mode": mode,
                    "label": label,
                    "confidence": round(conf, 2),
                    "bbox": [x, y, x + bw, y + bh],
                },
            }
            ingest_event(payload)

        # start
        post_state("start", base_sev)

        # ongoing
        steps = random.randint(steps_lo, steps_hi)
        sev = base_sev
        for _ in range(steps):
            time.sleep(random.uniform(0.6, 1.4))
            x += random.randint(-45, 45)
            y += random.randint(-25, 25)
            x = clamp(x, 20, 1100)
            y = clamp(y, 20, 600)

            conf = min(0.98, max(0.5, conf + random.uniform(-0.06, 0.06)))
            sev = clamp(sev + random.randint(3, 10), 0, 95)
            post_state("ongoing", sev)

        # peak
        post_state("peak", sev)
        time.sleep(random.uniform(0.8, 1.6))

        # end
        post_state("end", sev)

        # gap
        time.sleep(random.uniform(rate_lo, rate_hi))

if __name__ == "__main__":
    main()
