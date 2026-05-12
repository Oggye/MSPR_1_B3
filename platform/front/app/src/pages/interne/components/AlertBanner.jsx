import React from "react";

export default function AlertBanner({ level = "info", children }) {
  return <div className={`alert-banner ${level}`}>{children}</div>;
}
