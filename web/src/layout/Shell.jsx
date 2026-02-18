import React from "react";
import Sidebar from "./Sidebar.jsx";
import Topbar from "./Topbar.jsx";

export default function Shell({ children }) {
    return (
        <div className="app">
            <Sidebar />
            <div className="main">
                <Topbar />
                <div className="content">{children}</div>
            </div>
        </div>
    );
}
