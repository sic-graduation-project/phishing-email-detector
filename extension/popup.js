// Nexus toolbar popup: branding, how-to, status and a link to the web app.
// Scanning itself happens from the right-click menu (see background.js).
import { getExtensionStatus, openNexusWebApp } from "./api.js";

const statusEl = document.getElementById("status");
const statusText = document.getElementById("status-text");
const statusHint = document.getElementById("status-hint");
const demoBadge = document.getElementById("demo-badge");

document.getElementById("open-nexus").addEventListener("click", () => {
  openNexusWebApp();
  window.close();
});

getExtensionStatus().then((status) => {
  if (status.mode === "demo") {
    demoBadge.hidden = false;
    statusEl.classList.add("is-demo");
    statusText.textContent = "DEMO MODE";
    statusHint.textContent =
      "Results are simulated and no backend is used. To use the real API, set DEMO_MODE to false in config.js.";
    statusHint.hidden = false;
    return;
  }

  statusEl.classList.add(status.backendOnline ? "is-online" : "is-offline");
  statusText.textContent = status.backendOnline ? "Connected to the Nexus backend" : "Nexus backend is not reachable";
});
