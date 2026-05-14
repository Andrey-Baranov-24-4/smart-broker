import React from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App";

// Глушим «шумные» ошибки от @salutejs/client (WebSocket-ретраи в dev-режиме,
// отсутствие Salute-хоста и т.д.). Эти ошибки не влияют на работу приложения,
// но триггерят dev-overlay Create React App.
function isSaluteNoise(message) {
  if (!message) return false;
  const msg = String(message).toLowerCase();
  return (
    msg.includes("assistanthost") ||
    msg.includes("network error") ||
    msg.includes("websocket") ||
    msg.includes("'applicationid'") ||
    msg.includes("applicationid") ||
    msg === "[object event]"
  );
}

if (typeof window !== "undefined") {
  window.addEventListener("error", (event) => {
    if (isSaluteNoise(event.message) || isSaluteNoise(event.error?.message)) {
      event.preventDefault();
      event.stopImmediatePropagation();
    }
  });

  window.addEventListener("unhandledrejection", (event) => {
    const reason = event.reason;
    const text =
      typeof reason === "string"
        ? reason
        : reason?.message || reason?.type || String(reason);
    if (isSaluteNoise(text)) {
      event.preventDefault();
    }
  });
}

const container = document.getElementById("root");
const root = createRoot(container);
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
