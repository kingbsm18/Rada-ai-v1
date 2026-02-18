import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from .settings import settings
from .db import engine, Base

# IMPORTANT: force model import so SQLAlchemy registers tables
from . import models  # noqa: F401

from .routes.auth import router as auth_router
from .routes.dev import router as dev_router
from .routes.cameras import router as cameras_router
from .routes.events import router as events_router
from .routes.timeline import router as timeline_router
from fastapi.middleware.cors import CORSMiddleware



def ensure_dirs():
    os.makedirs(settings.MEDIA_DIR, exist_ok=True)
    os.makedirs(settings.SNAPSHOTS_DIR, exist_ok=True)
    os.makedirs(settings.CLIPS_DIR, exist_ok=True)
    os.makedirs(settings.RECORDINGS_DIR, exist_ok=True)


def create_app() -> FastAPI:
    ensure_dirs()

    app = FastAPI(title="rada-ai v1 backend")

   origins = [
  "http://localhost:5173",
  "https://demo.rada-ai.ma",
  "https://www.rada-ai.ma",
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

    app.mount("/media", StaticFiles(directory=settings.MEDIA_DIR), name="media")

    app.include_router(dev_router)
    app.include_router(auth_router)
    app.include_router(cameras_router)
    app.include_router(events_router)
    app.include_router(timeline_router)

    @app.on_event("startup")
    def on_startup():
        Base.metadata.create_all(bind=engine)

    @app.get("/")
    def root():
        return RedirectResponse(url="/docs")

    @app.get("/health")
    def health():
        return {"ok": True}

    return app


app = create_app()
