import React, { useMemo, useState } from "react";

export default function Live() {
    const cameras = useMemo(
        () => [
            { id: "cam_1", name: "Gate", mjpeg: "http://127.0.0.1:8088/cam_1.mjpg" },
            // later: cam_2..cam_4 (I can give you the script)
        ],
        []
    );

    const [selected, setSelected] = useState("cam_1");
    const cam = cameras.find((c) => c.id === selected) || cameras[0];

    return (
        <div className="panel">
            <div className="panel-head">
                <div>
                    <div className="h1">Live</div>
                    <div className="muted">Looped CCTV live feed (MJPEG)</div>
                </div>

                <select
                    className="select"
                    value={selected}
                    onChange={(e) => setSelected(e.target.value)}
                >
                    {cameras.map((c) => (
                        <option key={c.id} value={c.id}>
                            {c.name} ({c.id})
                        </option>
                    ))}
                </select>
            </div>

            <div className="live-wrap">
                <div className="live-tile">
                    <div className="live-head">
                        <div className="live-title">{cam.name}</div>
                        <div className="chip">MJPEG</div>
                    </div>

                    {/* MJPEG = use <img />, not <video> */}
                    <img className="live-img" src={cam.mjpeg} alt={cam.id} />

                    <div className="live-foot muted">
                        Source: {cam.mjpeg}
                    </div>
                </div>
            </div>
        </div>
    );
}
