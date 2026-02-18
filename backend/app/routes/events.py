from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Camera, Event
from ..schemas import EventIn, EventOut
from ..security import require_user

router = APIRouter(prefix="/events", tags=["events"])

def parse_ts(ts: str) -> datetime:
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(tzinfo=None)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ts format (expected ISO8601 ending with Z)")

@router.post("/ingest")
def ingest(payload: EventIn, db: Session = Depends(get_db)):
    """
    Ingest events from simulator:
    state: start/ongoing/peak/end
    """
    cam = db.query(Camera).filter(Camera.id == payload.camera_id).first()
    if not cam:
        raise HTTPException(status_code=400, detail="Invalid camera_id")

    state = payload.state
    ts = parse_ts(payload.ts)

    evt = db.query(Event).filter(Event.id == payload.event_id).first()

    if state == "start":
        if evt:
            return {"ok": True, "note": "already exists"}
        evt = Event(
            id=payload.event_id,
            camera_id=payload.camera_id,
            event_type=payload.event_type,
            severity=payload.severity,
            state="start",
            ts_start=ts,
            ts_peak=ts,
            snapshot_path=payload.snapshot_path,
            clip_path=payload.clip_path,
            meta=payload.meta or {},
        )
        db.add(evt)

    elif state in ("ongoing", "peak"):
        if not evt:
            raise HTTPException(status_code=404, detail="event not found")
        evt.state = state
        evt.severity = max(evt.severity, payload.severity)
        evt.ts_peak = ts
        if payload.snapshot_path:
            evt.snapshot_path = payload.snapshot_path
        if payload.clip_path:
            evt.clip_path = payload.clip_path
        if payload.meta is not None:
            evt.meta = payload.meta

    elif state == "end":
        if not evt:
            raise HTTPException(status_code=404, detail="event not found")
        evt.state = "end"
        evt.ts_end = ts
        evt.ts_peak = evt.ts_peak or ts
        if payload.snapshot_path:
            evt.snapshot_path = payload.snapshot_path
        if payload.clip_path:
            evt.clip_path = payload.clip_path
        if payload.meta is not None:
            evt.meta = payload.meta

    else:
        raise HTTPException(status_code=400, detail="Invalid state (start/ongoing/peak/end)")

    db.commit()
    return {"ok": True, "event_id": payload.event_id, "state": state}

@router.get("", response_model=list[EventOut])
def list_events(user=Depends(require_user), db: Session = Depends(get_db), limit: int = 200):
    events = db.query(Event).order_by(Event.ts_start.desc()).limit(min(limit, 500)).all()

    out = []
    for e in events:
        snapshot_url = f"/media/{e.snapshot_path}" if e.snapshot_path else None
        clip_url = f"/media/{e.clip_path}" if e.clip_path else None
        out.append(EventOut(
            id=e.id,
            camera_id=e.camera_id,
            event_type=e.event_type,
            severity=e.severity,
            state=e.state,
            ts_start=e.ts_start.isoformat(),
            ts_peak=e.ts_peak.isoformat() if e.ts_peak else None,
            ts_end=e.ts_end.isoformat() if e.ts_end else None,
            snapshot_url=snapshot_url,
            clip_url=clip_url,
            meta=e.meta or {},
        ))
    return out
