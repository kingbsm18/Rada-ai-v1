import React, { useEffect, useState } from "react";
import { login } from "../api/auth";

export default function Topbar() {
    const [status, setStatus] = useState("Not connected");

    useEffect(() => {
        // auto-login in mock mode (or if backend exists later)
        login("admin@rada.ai", "admin123")
            .then(() => setStatus("Connected"))
            .catch(() => setStatus("Offline (mock ok)"));
    }, []);

    return (
        <header className="topbar">
            <div className="topbar-title">Security Console</div>
            <div className="topbar-right">
                <span className="status">{status}</span>
            </div>
        </header>
    );
}
