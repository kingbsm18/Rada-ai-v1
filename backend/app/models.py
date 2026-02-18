from datetime import datetime
from sqlalchemy import Column, String, DateTime, Integer, JSON
from .db import Base

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(String, default="admin")
    school_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Camera(Base):
    __tablename__ = "cameras"
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    zone = Column(JSON, nullable=True)  # sim zones
    created_at = Column(DateTime, default=datetime.utcnow)

class Event(Base):
    __tablename__ = "events"
    id = Column(String, primary_key=True)

    camera_id = Column(String, nullable=False, index=True)

    event_type = Column(String, nullable=False)      # intrusion/loitering/...
    severity = Column(Integer, nullable=False)

    state = Column(String, nullable=False)           # start/ongoing/peak/end
    ts_start = Column(DateTime, nullable=False)
    ts_peak = Column(DateTime, nullable=True)
    ts_end = Column(DateTime, nullable=True)

    snapshot_path = Column(String, nullable=True)    # relative path under media/
    clip_path = Column(String, nullable=True)

    meta = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
