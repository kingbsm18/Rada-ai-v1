import os
import random
import subprocess
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO
from typing import Optional, List

import imageio_ffmpeg
from PIL import Image, ImageDraw

# ─── Colors ───────────────────────────────────────────────────────────────────
COLOR_PERSON  = (0, 210, 120)
COLOR_PHONE   = (255, 60,  60)
COLOR_ZONE    = (80, 180, 255)
HEADER_BG     = (10, 10, 12)
GRID_COLOR    = (24, 24, 30)


# ─── ffmpeg helpers ───────────────────────────────────────────────────────────

def _ffmpeg_bin() -> str:
    return imageio_ffmpeg.get_ffmpeg_exe()

def ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)

def ffprobe_duration_seconds(video_path: str) -> Optional[float]:
    ff = _ffmpeg_bin()
    try:
        p = subprocess.run([ff, "-i", video_path],
                           stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        s = p.stderr or ""
        key = "Duration: "
        idx = s.find(key)
        if idx == -1:
            return None
        dur = s[idx + len(key): idx + len(key) + 11]
        hh = int(dur[0:2]); mm = int(dur[3:5]); ss = float(dur[6:])
        return hh * 3600 + mm * 60 + ss
    except Exception:
        return None

def ffmpeg_snapshot(video_path: str, out_jpg: str, t_sec: float) -> bool:
    ensure_dir(os.path.dirname(out_jpg))
    ff = _ffmpeg_bin()
    cmd = [ff, "-y", "-ss", str(max(0.0, t_sec)), "-i", video_path,
           "-frames:v", "1", "-q:v", "2", out_jpg]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception:
        return False


# ─── Mock detection state ─────────────────────────────────────────────────────

class _DetectionState:
    """
    Holds mock person/phone detections.
    Refreshes every REFRESH_SEC so boxes move naturally.
    """
    REFRESH_SEC = 4.0

    def __init__(self, width: int, height: int):
        self.width  = width
        self.height = height
        self._lock  = threading.Lock()
        self._persons: List[dict] = []
        self._last_refresh = 0.0
        self._rng = random.Random()
        self._refresh()

    def _refresh(self):
        rng = self._rng
        n_persons = rng.randint(3, 8)
        n_phones  = rng.randint(0, max(1, n_persons // 3))

        persons = []
        for i in range(n_persons):
            pw = rng.randint(55, 110)
            ph = rng.randint(int(pw * 1.8), int(pw * 2.6))
            x1 = rng.randint(10, max(11, self.width  - pw - 10))
            y1 = rng.randint(115, max(116, self.height - ph - 10))
            persons.append({
                "x1": x1, "y1": y1,
                "x2": x1 + pw, "y2": y1 + ph,
                "conf": round(rng.uniform(0.72, 0.98), 2),
                "has_phone": False,
            })

        for p in rng.sample(persons, min(n_phones, len(persons))):
            p["has_phone"] = True

        with self._lock:
            self._persons = persons
            self._last_refresh = time.time()

    def _nudge(self):
        """Slightly move boxes every frame so they feel alive."""
        rng = self._rng
        with self._lock:
            for p in self._persons:
                dx = rng.randint(-2, 2)
                dy = rng.randint(-1, 1)
                w = p["x2"] - p["x1"]
                h = p["y2"] - p["y1"]
                p["x1"] = max(10, min(self.width  - w - 10,  p["x1"] + dx))
                p["x2"] = p["x1"] + w
                p["y1"] = max(115, min(self.height - h - 10, p["y1"] + dy))
                p["y2"] = p["y1"] + h

    def get(self) -> List[dict]:
        if time.time() - self._last_refresh > self.REFRESH_SEC:
            self._refresh()
        else:
            self._nudge()
        with self._lock:
            return list(self._persons)


# ─── Overlay drawing ──────────────────────────────────────────────────────────

def _draw_person(draw: ImageDraw.Draw, p: dict):
    x1, y1, x2, y2 = p["x1"], p["y1"], p["x2"], p["y2"]
    conf  = p["conf"]
    color = COLOR_PHONE if p["has_phone"] else COLOR_PERSON

    # Bounding box
    draw.rectangle([x1, y1, x2, y2], outline=color, width=2)

    # Head circle
    head_r = max(8, (x2 - x1) // 4)
    cx = (x1 + x2) // 2
    draw.ellipse([cx - head_r, y1 - head_r * 2,
                  cx + head_r, y1], outline=color, width=2)

    # Confidence label
    label = f"Person {conf:.2f}"
    lx = x1
    ly = max(0, y1 - head_r * 2 - 18)
    draw.rectangle([lx, ly, lx + len(label) * 7 + 6, ly + 16], fill=(0, 0, 0))
    draw.text((lx + 3, ly + 2), label, fill=color)

    if p["has_phone"]:
        _draw_phone(draw, p)


def _draw_phone(draw: ImageDraw.Draw, p: dict):
    x1, y1, x2, y2 = p["x1"], p["y1"], p["x2"], p["y2"]
    pw   = x2 - x1
    ph_w = max(18, pw // 3)
    ph_h = max(30, ph_w * 2)
    cx   = (x1 + x2) // 2
    py1  = max(y1, y1 + (y2 - y1) * 2 // 3 - ph_h // 2)
    py2  = min(y2, py1 + ph_h)
    px1  = max(x1, cx - ph_w // 2)
    px2  = min(x2, cx + ph_w // 2)

    draw.rectangle([px1, py1, px2, py2], outline=COLOR_PHONE, width=2)

    inner = 3
    if px2 - px1 > inner * 3 and py2 - py1 > inner * 3:
        draw.rectangle([px1 + inner, py1 + inner,
                        px2 - inner, py2 - inner],
                       outline=(200, 40, 40), width=1)

    lx = max(x1, px1 - 4)
    ly = max(0, py1 - 16)
    draw.rectangle([lx, ly, lx + 68, ly + 14], fill=(40, 0, 0))
    draw.text((lx + 3, ly + 2), "Phone \U0001f4f1", fill=COLOR_PHONE)


def _draw_header(draw: ImageDraw.Draw, w: int,
                 cam_name: str, n_persons: int, n_phones: int):
    draw.rectangle([0, 0, w, 100], fill=HEADER_BG)
    draw.text((16, 10), f"RADA AI v1  |  {cam_name}", fill=(255, 255, 255))

    phone_txt = f"  \u26a0 {n_phones} phone(s) detected" if n_phones > 0 else ""
    draw.text((16, 36),
              f"Persons: {n_persons}{phone_txt}",
              fill=COLOR_PHONE if n_phones > 0 else COLOR_PERSON)

    draw.text((16, 62),
              "LIVE  \u2022  MJPEG  \u2022  SIMULATED FEED",
              fill=(80, 80, 80))

    # REC indicator
    draw.ellipse([w - 80, 14, w - 62, 32], fill=(220, 40, 40))
    draw.text((w - 56, 14), "REC", fill=(220, 40, 40))


def _apply_overlay(frame_bytes: bytes,
                   detection: "_DetectionState",
                   cam_name: str) -> bytes:
    try:
        img = Image.open(BytesIO(frame_bytes)).convert("RGB")
        w, h = img.size
        draw = ImageDraw.Draw(img)

        persons  = detection.get()
        n_phones = sum(1 for p in persons if p["has_phone"])

        for p in persons:
            _draw_person(draw, p)

        _draw_header(draw, w, cam_name, len(persons), n_phones)

        buf = BytesIO()
        img.save(buf, format="JPEG", quality=82)
        return buf.getvalue()
    except Exception:
        return frame_bytes   # fallback: original frame untouched


# ─── Frame buffer ─────────────────────────────────────────────────────────────

class _FrameBuffer:
    def __init__(self):
        self._frame: Optional[bytes] = None
        self._lock  = threading.Lock()
        self._event = threading.Event()

    def put(self, frame: bytes):
        with self._lock:
            self._frame = frame
        self._event.set()
        self._event.clear()

    def get(self) -> Optional[bytes]:
        with self._lock:
            return self._frame

    def wait(self, timeout=5.0):
        self._event.wait(timeout)


_buffer    = _FrameBuffer()
_detection: Optional[_DetectionState] = None
_cam_name  = "Camera"


def _ffmpeg_reader(video_path: str, fps: int, width: int):
    """Read frames from ffmpeg, apply overlay, push to buffer. Loops forever."""
    ff  = _ffmpeg_bin()
    SOI = b"\xff\xd8"
    EOI = b"\xff\xd9"

    while True:
        cmd = [
            ff, "-re", "-i", video_path,
            "-vf", f"scale={width}:-1,fps={fps}",
            "-f", "image2pipe",
            "-vcodec", "mjpeg",
            "-q:v", "5",
            "pipe:1",
        ]
        try:
            proc = subprocess.Popen(cmd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.DEVNULL)
            buf = b""
            while True:
                chunk = proc.stdout.read(8192)
                if not chunk:
                    break
                buf += chunk

                while True:
                    start = buf.find(SOI)
                    if start == -1:
                        buf = b""
                        break
                    end = buf.find(EOI, start + 2)
                    if end == -1:
                        buf = buf[start:]
                        break
                    raw = buf[start: end + 2]
                    buf = buf[end + 2:]

                    if _detection is not None:
                        raw = _apply_overlay(raw, _detection, _cam_name)

                    _buffer.put(raw)

            proc.wait()
        except Exception as e:
            print(f"[MJPEG] reader error: {e}")
            time.sleep(1)
        # video ended → loop back


# ─── HTTP handler ─────────────────────────────────────────────────────────────

class _MJPEGHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type",
                         "multipart/x-mixed-replace; boundary=frame")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        try:
            while True:
                frame = _buffer.get()
                if frame is None:
                    _buffer.wait(timeout=2.0)
                    continue
                self.wfile.write(
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n"
                    + frame + b"\r\n"
                )
                self.wfile.flush()
                time.sleep(0.05)
        except (BrokenPipeError, ConnectionResetError):
            pass


# ─── Public API ───────────────────────────────────────────────────────────────

def start_mjpeg_server(
    video_path: str,
    host: str = "127.0.0.1",
    port: int = 8088,
    fps: int = 10,
    width: int = 1280,
    cam_name: str = "Gate (cam_1)",
):
    global _detection, _cam_name
    _cam_name = cam_name

    reader = threading.Thread(
        target=_ffmpeg_reader,
        args=(video_path, fps, width),
        daemon=True,
    )
    reader.start()

    print("[MJPEG] Waiting for first frame from ffmpeg...")
    _buffer.wait(timeout=10.0)
    if _buffer.get() is None:
        raise RuntimeError("ffmpeg produced no frames — check your video path.")

    # Init detection with actual frame size
    _detection = _DetectionState(width=width, height=int(width * 9 / 16))

    server = HTTPServer((host, port), _MJPEGHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    print(f"[MJPEG] Live feed + overlay → http://{host}:{port}/cam_1.mjpg")
    return server