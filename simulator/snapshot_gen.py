import os
import random
from typing import Tuple, List, Optional
from PIL import Image, ImageDraw, ImageFilter

# ─── Palette ──────────────────────────────────────────────────────────────────
BG_COLOR        = (14, 14, 18)
GRID_COLOR      = (24, 24, 30)
HEADER_COLOR    = (10, 10, 12)

# Detection colors
COLOR_PERSON    = (0, 210, 120)    # green
COLOR_PHONE     = (255, 60,  60)   # red  ← threat
COLOR_PEAK      = (255, 180,  0)   # amber
COLOR_END       = (160, 160, 160)  # grey

LABEL_BG        = (0, 0, 0, 160)   # semi-transparent


# ─── Mock scene generator ─────────────────────────────────────────────────────

def _random_persons(n: int, width: int, height: int, seed: int) -> List[dict]:
    """
    Generate n plausible person bounding boxes spread across the scene.
    Each person is a portrait-aspect rectangle.
    """
    rng = random.Random(seed)
    persons = []
    for i in range(n):
        pw = rng.randint(60, 140)
        ph = rng.randint(int(pw * 1.8), int(pw * 2.8))
        x1 = rng.randint(10, max(11, width - pw - 10))
        y1 = rng.randint(120, max(121, height - ph - 10))
        persons.append({
            "id": i,
            "x1": x1, "y1": y1,
            "x2": x1 + pw, "y2": y1 + ph,
            "conf": round(rng.uniform(0.72, 0.98), 2),
            "has_phone": False,
        })
    return persons


def _pick_phone_holders(persons: List[dict], n_phones: int, seed: int) -> List[dict]:
    """Mark some persons as holding a phone."""
    rng = random.Random(seed + 99)
    chosen = rng.sample(persons, min(n_phones, len(persons)))
    for p in chosen:
        p["has_phone"] = True
    return persons


def _draw_person(draw: ImageDraw.Draw, p: dict, state: str, show_phone: bool):
    """Draw a person bounding box with label."""
    x1, y1, x2, y2 = p["x1"], p["y1"], p["x2"], p["y2"]
    conf = p["conf"]

    if state == "peak":
        box_color = COLOR_PEAK
    elif state == "end":
        box_color = COLOR_END
    else:
        box_color = COLOR_PERSON

    # Person box
    draw.rectangle([x1, y1, x2, y2], outline=box_color, width=2)

    # Skeleton hint: head circle
    head_r = max(8, (x2 - x1) // 4)
    cx = (x1 + x2) // 2
    draw.ellipse(
        [cx - head_r, y1 - head_r * 2, cx + head_r, y1],
        outline=box_color, width=2
    )

    # Label chip
    label_text = f"Person {conf:.2f}"
    lx, ly = x1, max(0, y1 - head_r * 2 - 18)
    draw.rectangle([lx, ly, lx + len(label_text) * 7 + 6, ly + 16],
                   fill=(0, 0, 0))
    draw.text((lx + 3, ly + 2), label_text, fill=box_color)

    # Phone indicator inside the box
    if show_phone and p["has_phone"]:
        _draw_phone_box(draw, p, state)


def _draw_phone_box(draw: ImageDraw.Draw, p: dict, state: str):
    """Draw a small phone detection box inside/near the person box."""
    x1, y1, x2, y2 = p["x1"], p["y1"], p["x2"], p["y2"]

    # Phone is at chest/hand level — lower third of person box
    pw = x2 - x1
    ph_box_w = max(20, pw // 3)
    ph_box_h = max(32, ph_box_w * 2)

    # Center horizontally, place at lower portion
    cx = (x1 + x2) // 2
    py1 = y1 + (y2 - y1) * 2 // 3 - ph_box_h // 2
    py2 = py1 + ph_box_h
    px1 = cx - ph_box_w // 2
    px2 = cx + ph_box_w // 2

    # Clamp to person box
    py1 = max(y1, py1); py2 = min(y2, py2)
    px1 = max(x1, px1); px2 = min(x2, px2)

    # Draw phone bounding box
    draw.rectangle([px1, py1, px2, py2], outline=COLOR_PHONE, width=2)

    # Rounded screen representation (just a smaller rectangle)
    inner = 3
    if px2 - px1 > inner * 3 and py2 - py1 > inner * 3:
        draw.rectangle(
            [px1 + inner, py1 + inner, px2 - inner, py2 - inner],
            outline=(*COLOR_PHONE, 120), width=1
        )

    # Label chip above phone box
    phone_label = "Phone 📱"
    lx = max(x1, px1 - 4)
    ly = max(0, py1 - 16)
    draw.rectangle([lx, ly, lx + 68, ly + 14], fill=(40, 0, 0))
    draw.text((lx + 3, ly + 2), phone_label, fill=COLOR_PHONE)


def _draw_scene_noise(draw: ImageDraw.Draw, width: int, height: int):
    """Add subtle grid and scanlines for CCTV feel."""
    # Grid
    for x in range(0, width, 80):
        draw.line([(x, 0), (x, height)], fill=GRID_COLOR, width=1)
    for y in range(0, height, 80):
        draw.line([(0, y), (width, y)], fill=GRID_COLOR, width=1)

    # Scanlines (every 4px, very subtle)
    for y in range(0, height, 4):
        draw.line([(0, y), (width, y)], fill=(0, 0, 0, 30), width=1)


def _draw_header(draw: ImageDraw.Draw, width: int,
                 cam_name: str, event_id: str, label: str,
                 conf: float, severity: int, state: str,
                 n_persons: int, n_phones: int):
    """Draw the top info bar."""
    if state == "peak":
        accent = COLOR_PEAK
    elif state == "end":
        accent = COLOR_END
    else:
        accent = COLOR_PERSON

    draw.rectangle([0, 0, width, 110], fill=HEADER_COLOR)

    # Row 1
    draw.text((16, 10), f"RADA AI v1  |  {cam_name}", fill=(255, 255, 255))

    # Row 2 — event info
    row2 = f"{label}  conf={conf:.2f}  severity={severity}  state={state.upper()}"
    draw.text((16, 36), row2, fill=accent)

    # Row 3 — detections summary
    phone_txt = f"  ⚠ {n_phones} phone(s) detected" if n_phones > 0 else ""
    row3 = f"Persons: {n_persons}{phone_txt}"
    draw.text((16, 62), row3, fill=COLOR_PHONE if n_phones > 0 else (180, 180, 180))

    # Row 4 — event id
    draw.text((16, 86), f"event={event_id}", fill=(120, 120, 120))

    # Right side: REC dot
    draw.ellipse([width - 80, 18, width - 62, 36], fill=(220, 40, 40))
    draw.text((width - 56, 18), "REC", fill=(220, 40, 40))


def _draw_main_bbox(draw: ImageDraw.Draw, bbox: Tuple, state: str):
    """Draw the original event zone/bbox (zone of interest)."""
    x1, y1, x2, y2 = bbox
    if state == "peak":
        color = COLOR_PEAK
    elif state == "end":
        color = COLOR_END
    else:
        color = (80, 180, 255)   # blue zone of interest

    # Dashed-style via segments
    dash = 12
    gap = 6
    def dashed_line(p1, p2):
        x0, y0 = p1; xn, yn = p2
        dx = xn - x0; dy = yn - y0
        length = max(abs(dx), abs(dy))
        if length == 0: return
        steps = length // (dash + gap)
        for i in range(steps + 1):
            t0 = i * (dash + gap) / length
            t1 = min(1.0, t0 + dash / length)
            sx = int(x0 + dx * t0); sy = int(y0 + dy * t0)
            ex = int(x0 + dx * t1); ey = int(y0 + dy * t1)
            draw.line([(sx, sy), (ex, ey)], fill=color, width=1)

    dashed_line((x1, y1), (x2, y1))
    dashed_line((x2, y1), (x2, y2))
    dashed_line((x2, y2), (x1, y2))
    dashed_line((x1, y2), (x1, y1))

    # Corner accents
    cs = 14
    draw.line([(x1, y1), (x1 + cs, y1)], fill=color, width=3)
    draw.line([(x1, y1), (x1, y1 + cs)], fill=color, width=3)
    draw.line([(x2, y1), (x2 - cs, y1)], fill=color, width=3)
    draw.line([(x2, y1), (x2, y1 + cs)], fill=color, width=3)
    draw.line([(x1, y2), (x1 + cs, y2)], fill=color, width=3)
    draw.line([(x1, y2), (x1, y2 - cs)], fill=color, width=3)
    draw.line([(x2, y2), (x2 - cs, y2)], fill=color, width=3)
    draw.line([(x2, y2), (x2, y2 - cs)], fill=color, width=3)

    # Zone label
    draw.text((x1 + 4, y1 + 4), "ZONE", fill=color)


# ─── Public API ───────────────────────────────────────────────────────────────

def generate_snapshot(
    out_path: str,
    cam_name: str,
    event_id: str,
    label: str,
    conf: float,
    bbox: Tuple[int, int, int, int],
    severity: int,
    state: str,
    width: int = 1280,
    height: int = 720,
    n_persons: Optional[int] = None,
    n_phones: Optional[int] = None,
) -> None:
    os.makedirs(os.path.dirname(out_path), exist_ok=True)

    # Deterministic randomness based on event_id so the same event
    # always produces the same layout
    seed = hash(event_id) & 0xFFFFFF

    rng = random.Random(seed)

    # Decide number of people / phones based on severity
    if n_persons is None:
        n_persons = rng.randint(2, max(2, severity // 12 + 2))
    if n_phones is None:
        # More phones possible at higher severity
        max_phones = max(0, min(n_persons, severity // 25))
        n_phones = rng.randint(0, max_phones)

    # ── Draw background
    img = Image.new("RGB", (width, height), BG_COLOR)
    draw = ImageDraw.Draw(img, "RGBA")

    _draw_scene_noise(draw, width, height)

    # ── Draw zone of interest (dashed bbox)
    _draw_main_bbox(draw, bbox, state)

    # ── Generate & draw persons
    persons = _random_persons(n_persons, width, height, seed)
    persons = _pick_phone_holders(persons, n_phones, seed)

    for p in persons:
        _draw_person(draw, p, state, show_phone=True)

    # ── Header bar (drawn last so it's always on top)
    _draw_header(
        draw, width,
        cam_name, event_id, label, conf, severity, state,
        n_persons, n_phones
    )

    # ── Slight blur for realism
    img = img.filter(ImageFilter.GaussianBlur(radius=0.4))

    img.save(out_path, "JPEG", quality=88)