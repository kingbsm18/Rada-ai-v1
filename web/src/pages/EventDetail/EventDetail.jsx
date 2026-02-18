import React, { useEffect, useMemo, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { getEvents } from "../../api/events";
import Spinner from "../../components/Spinner.jsx";
import EmptyState from "../../components/EmptyState.jsx";
import Badge from "../../components/Badge.jsx";

export default function EventDetail() {
    const { id } = useParams();
    const nav = useNavigate();
    const [loading, setLoading] = useState(true);
    const [events, setEvents] = useState([]);

    useEffect(() => {
        let alive = true;
        getEvents(200)
            .then((ev) => alive && setEvents(ev))
            .finally(() => alive && setLoading(false));
        return () => (alive = false);
    }, []);

    const evt = useMemo(() => events.find((e) => e.id === id), [events, id]);

    if (loading) return <Spinner label="Loading event..." />;
    if (!evt) return <EmptyState title="Event not found" subtitle="It may have expired or not loaded yet." />;

    return (
        <div className="detail">
            <div className="detail-head">
                <button className="btn" onClick={() => nav(-1)}>← Back</button>
                <div>
                    <div className="h1">{evt.event_type}</div>
                    <div className="muted">Event ID: {evt.id}</div>
                </div>
                <Badge value={evt.state} />
            </div>

            <div className="detail-body">
                <div className="box">
                    <div className="box-title">Snapshot</div>
                    {evt.snapshot_url ? (
                        <img className="detail-img" src={`http://127.0.0.1:8000${evt.snapshot_url}`} alt="snapshot" />
                    ) : (
                        <div className="detail-img placeholder">No snapshot (mock)</div>
                    )}
                </div>

                <div className="box">
                    <div className="box-title">Metadata</div>
                    <pre className="code">{JSON.stringify(evt, null, 2)}</pre>
                </div>
            </div>
        </div>
    );
}
