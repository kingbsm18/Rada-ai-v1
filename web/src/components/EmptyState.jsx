import React from "react";

export default function EmptyState({ title, subtitle }) {
    return (
        <div className="center">
            <div className="h1">{title}</div>
            <div className="muted" style={{ marginTop: 8, maxWidth: 520, textAlign: "center" }}>
                {subtitle}
            </div>
        </div>
    );
}
