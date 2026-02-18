import React from "react";
import { NavLink } from "react-router-dom";

export default function Sidebar() {
    return (
        <aside className="sidebar">
            <div className="brand">
                <div className="logo-dot" />
                <div>
                    <div className="brand-title">RADA AI</div>
                    <div className="brand-sub">v1</div>
                </div>
            </div>

            <nav className="nav">
                <NavLink to="/live" className={({ isActive }) => (isActive ? "nav-item active" : "nav-item")}>Live</NavLink>
                <NavLink to="/review" className={({ isActive }) => (isActive ? "nav-item active" : "nav-item")}>Review</NavLink>
                <NavLink to="/system" className={({ isActive }) => (isActive ? "nav-item active" : "nav-item")}>System</NavLink>
                <NavLink to="/config" className={({ isActive }) => (isActive ? "nav-item active" : "nav-item")}>Config</NavLink>
            </nav>

            <div className="sidebar-foot">
                <div className="chip">Mode: {import.meta.env.VITE_API_MODE || "mock"}</div>
            </div>
        </aside>
    );
}
