from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"

class CameraOut(BaseModel):
    id: str
    name: str
    zone: Optional[Dict[str, Any]] = None

class EventIn(BaseModel):
    event_id: str
    camera_id: str
    event_type: str
    severity: int = Field(ge=0, le=100)
    state: str  # start/ongoing/peak/end
    ts: str     # ISO8601 "....Z"
    snapshot_path: Optional[str] = None
    clip_path: Optional[str] = None
    meta: Optional[Dict[str, Any]] = None

class EventOut(BaseModel):
    id: str
    camera_id: str
    event_type: str
    severity: int
    state: str
    ts_start: str
    ts_peak: Optional[str] = None
    ts_end: Optional[str] = None
    snapshot_url: Optional[str] = None
    clip_url: Optional[str] = None
    meta: Dict[str, Any] = {}
