from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import Camera
from ..security import require_user
from ..schemas import CameraOut

router = APIRouter(prefix="/cameras", tags=["cameras"])

@router.get("", response_model=list[CameraOut])
def list_cameras(user=Depends(require_user), db: Session = Depends(get_db)):
    cams = db.query(Camera).order_by(Camera.created_at.asc()).all()
    return [CameraOut(id=c.id, name=c.name, zone=c.zone) for c in cams]
