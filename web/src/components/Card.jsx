import React from "react";

export default function Card({ children, onClick }) {
    return (
        <div className="card" onClick={onClick} role="button" tabIndex={0}>
            {children}
        </div>
    );
}
