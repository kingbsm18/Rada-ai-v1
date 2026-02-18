from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from ..db import get_db
from ..models import User, Camera
from ..security import hash_password

router = APIRouter(prefix="/dev", tags=["dev"])

@router.post("/seed")
def seed(db: Session = Depends(get_db)):
    try:
        # Ensure password is within bcrypt's 72-byte limit
        admin_password = "admin123"
        if len(admin_password.encode("utf-8")) > 72:
            admin_password = admin_password.encode("utf-8")[:72].decode("utf-8", errors="ignore")
        
        admin = User(
            id="admin_1",
            email="admin@rada.ai",
            password_hash=hash_password(admin_password),
            role="admin",
            school_id=None,
        )
        cams = [
            Camera(id="cam_1", name="Gate", zone={"type":"rect","x":0.1,"y":0.1,"w":0.8,"h":0.8}),
            Camera(id="cam_2", name="Yard", zone={"type":"rect","x":0.2,"y":0.2,"w":0.6,"h":0.6}),
            Camera(id="cam_3", name="Hallway", zone={"type":"rect","x":0.15,"y":0.15,"w":0.7,"h":0.7}),
            Camera(id="cam_4", name="Parking", zone={"type":"rect","x":0.1,"y":0.2,"w":0.7,"h":0.6}),
        ]
        db.add(admin)
        db.add_all(cams)
        db.commit()
        return {"ok": True, "admin": {"email":"admin@rada.ai","password":"admin123"}}
    except IntegrityError:
        db.rollback()
        return {"ok": True, "note": "Already seeded"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Seed failed: {type(e).__name__}: {e}")