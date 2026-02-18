import React from "react";
import { Routes, Route, Navigate } from "react-router-dom";
import Shell from "../layout/Shell.jsx";
import Live from "../pages/Live/Live.jsx";
import Review from "../pages/Review/Review.jsx";
import EventDetail from "../pages/EventDetail/EventDetail.jsx";
import System from "../pages/System/System.jsx";
import Config from "../pages/Config/Config.jsx";

export default function App() {
  return (
    <Shell>
      <Routes>
        <Route path="/" element={<Navigate to="/review" replace />} />
        <Route path="/live" element={<Live />} />
        <Route path="/review" element={<Review />} />
        <Route path="/events/:id" element={<EventDetail />} />
        <Route path="/system" element={<System />} />
        <Route path="/config" element={<Config />} />
      </Routes>
    </Shell>
  );
}
