from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Event
from ..security import require_user

router = APIRouter(prefix="/timeline", tags=["timeline"])

@router.get("/{camera_id}")
def timeline(camera_id: str, user=Depends(require_user), db: Session = Depends(get_db), limit: int = 300):
    ev = (
        db.query(Event)
        .filter(Event.camera_id == camera_id)
        .order_by(Event.ts_start.desc())
        .limit(min(limit, 1000))
        .all()
    )
    return [
        {
            "id": e.id,
            "event_type": e.event_type,
            "severity": e.severity,
            "state": e.state,
            "ts_start": e.ts_start.isoformat(),
            "ts_end": e.ts_end.isoformat() if e.ts_end else None,
        }
        for e in ev
    ]
