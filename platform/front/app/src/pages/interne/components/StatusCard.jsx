import React from "react";

export default function StatusCard({ label, value, detail, status = "neutral" }) {
  return (
    <article className={`status-card ${status}`}>
      <div className="status-topline">
        <span className="status-dot" />
        <span>{label}</span>
      </div>
      <strong>{value}</strong>
      {detail && <small>{detail}</small>}
    </article>
  );
}
