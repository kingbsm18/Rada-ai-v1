"""
Quick test: generates sample snapshots for each state.
Run from the simulator folder:
    python test_snapshot.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from snapshot_gen import generate_snapshot

os.makedirs("test_snapshots", exist_ok=True)

cases = [
    ("start",   45, "evt_a1b2c3d4e5", "Loitering",  0.81),
    ("ongoing", 65, "evt_f6g7h8i9j0", "Intrusion",  0.90),
    ("peak",    88, "evt_k1l2m3n4o5", "Phone Use",  0.94),
    ("end",     88, "evt_p6q7r8s9t0", "Loitering",  0.76),
]

for state, severity, eid, label, conf in cases:
    out = f"test_snapshots/{state}_{label.replace(' ','_')}.jpg"
    generate_snapshot(
        out_path=out,
        cam_name="Gate",
        event_id=eid,
        label=label,
        conf=conf,
        bbox=(200, 150, 900, 600),
        severity=severity,
        state=state,
    )
    print(f"✓ {out}")

print("\nDone! Check the test_snapshots/ folder.")