import React from "react";

export default function Badge({ value }) {
    const v = String(value || "").toLowerCase();
    const cls =
        v === "peak" ? "badge warn" :
            v === "end" ? "badge neutral" :
                "badge ok";

    return <span className={cls}>{value}</span>;
}
