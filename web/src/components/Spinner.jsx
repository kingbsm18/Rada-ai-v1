import React from "react";

export default function Spinner({ label = "Loading..." }) {
    return (
        <div className="center">
            <div className="spinner" />
            <div className="muted" style={{ marginTop: 10 }}>{label}</div>
        </div>
    );
}
