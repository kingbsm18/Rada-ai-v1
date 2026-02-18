import React, { useEffect, useMemo, useState } from "react";
import { getEvents } from "../../api/events";
import { getCameras } from "../../api/cameras";
import Card from "../../components/Card.jsx";
import Badge from "../../components/Badge.jsx";
import Spinner from "../../components/Spinner.jsx";
import EmptyState from "../../components/EmptyState.jsx";
import { useNavigate } from "react-router-dom";

export default function Review() {
    const [loading, setLoading] = useState(true);
    const [events, setEvents] = useState([]);
    const [cameras, setCameras] = useState([]);
    const [filterCam, setFilterCam] = useState("all");
    const navigate = useNavigate();

    useEffect(() => {
        let alive = true;
        async function load() {
            try {
                const [cams, ev] = await Promise.all([getCameras(), getEvents(200)]);
                if (!alive) return;
                setCameras(cams);
                setEvents(ev);
            } finally {
                if (alive) setLoading(false);
            }
        }
        load();
        const t = setInterval(load, 2500); // refresh like Frigate
        return () => {
            alive = false;
            clearInterval(t);
        };
    }, []);

    const filtered = useMemo(() => {
        if (filterCam === "all") return events;
        return events.filter((e) => e.camera_id === filterCam);
    }, [events, filterCam]);

    if (loading) return <Spinner label="Loading events..." />;
    if (!filtered.length) return <EmptyState title="No events yet" subtitle="Start the simulator or switch to API mode." />;

    return (
        <div className="grid">
            <div className="panel">
                <div className="panel-head">
                    <div>
                        <div className="h1">Review</div>
                        <div className="muted">Timeline of detections & incidents</div>
                    </div>

                    <select className="select" value={filterCam} onChange={(e) => setFilterCam(e.target.value)}>
                        <option value="all">All cameras</option>
                        {cameras.map((c) => (
                            <option key={c.id} value={c.id}>
                                {c.name} ({c.id})
                            </option>
                        ))}
                    </select>
                </div>

                <div className="cards">
                    {filtered.slice(0, 60).map((e) => (
                        <Card key={e.id} onClick={() => navigate(`/events/${e.id}`)}>
                            <div className="card-row">
                                <div>
                                    <div className="card-title">{e.event_type}</div>
                                    <div className="muted">Camera: {e.camera_id}</div>
                                </div>
                                <Badge value={e.state} />
                            </div>

                            <div className="card-meta">
                                <div className="muted">Severity: {e.severity}</div>
                                <div className="muted">{new Date(e.ts_start).toLocaleString()}</div>
                            </div>

                            {e.snapshot_url ? (
                                <img className="thumb" src={`http://127.0.0.1:8000${e.snapshot_url}`} alt="snapshot" />
                            ) : (
                                <div className="thumb placeholder">
                                    <div className="muted">No snapshot (mock)</div>
                                </div>
                            )}
                        </Card>
                    ))}
                </div>
            </div>
        </div>
    );
}
