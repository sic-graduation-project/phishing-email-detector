// Nexus result window.
//
// Shows the loading state, then the backend's answer (classification, risk
// score, reasons) for the scan started from the right-click menu. All values
// are written with textContent, never as HTML: backend text is untrusted.
import { RETRYABLE_CODES, canOpenWithInput, errorMessage, isDemoMode, openNexusWebApp } from "./api.js";

const byId = (id) => document.getElementById(id);
const demo = isDemoMode();
const el = {
  tagline: byId("tagline"),
  demoBadge: byId("demo-badge"),
  demoNote: byId("demo-note"),
  moreNote: byId("more-note"),
  scanned: byId("scanned"),
  scannedLabel: byId("scanned-label"),
  scannedPreview: byId("scanned-preview"),
  loading: byId("loading"),
  result: byId("result"),
  verdict: byId("verdict"),
  scoreValue: byId("score-value"),
  meter: byId("meter"),
  meterFill: byId("meter-fill"),
  reasonsList: byId("reasons-list"),
  reasonsEmpty: byId("reasons-empty"),
  message: byId("message"),
  retryBtn: byId("retry-btn"),
  viewBtn: byId("view-btn"),
};

const scanId = new URLSearchParams(location.search).get("id");
let currentRev = 0;
let currentView = null;

function show(element, visible) {
  element.hidden = !visible;
}

// Maps the backend's classification label to a color. Labels other than
// "Phishing" / "Legitimate" are shown as-is with a neutral style.
function verdictStyle(classification) {
  const key = classification.toLowerCase();
  if (key === "phishing") return { className: "is-phishing", icon: "⚠︎" };
  if (key === "legitimate") return { className: "is-safe", icon: "✓" };
  return { className: "is-neutral", icon: "ℹ︎" };
}

function renderHeading(view) {
  const heading = view.kind === "url" ? "URL Analysis" : "Text Analysis";
  el.tagline.textContent = heading;
  document.title = `Nexus - ${heading}${demo ? " (Demo Mode)" : ""}`;
}

function renderScanned(view) {
  const hasPreview = typeof view.preview === "string" && view.preview !== "";
  show(el.scanned, hasPreview);
  if (!hasPreview) return;
  el.scannedLabel.textContent = view.kind === "url" ? "Scanned link" : "Scanned text";
  el.scannedPreview.textContent = view.preview;
  el.scannedPreview.classList.toggle("is-link", view.kind === "url");
}

function renderResult({ classification, riskScore, reasons }) {
  const style = verdictStyle(classification);
  el.result.className = `result ${style.className}`;
  el.verdict.textContent = `${style.icon} ${classification}`;

  if (riskScore === null) {
    el.scoreValue.textContent = "N/A";
    el.meterFill.style.width = "0%";
    el.meter.removeAttribute("aria-valuenow");
  } else {
    el.scoreValue.textContent = `${Math.round(riskScore)}%`;
    el.meterFill.style.width = `${riskScore}%`;
    el.meter.setAttribute("aria-valuenow", String(riskScore));
  }

  el.reasonsList.replaceChildren(
    ...reasons.map((reason) => {
      const item = document.createElement("li");
      item.textContent = reason;
      return item;
    })
  );
  show(el.reasonsList, reasons.length > 0);
  show(el.reasonsEmpty, reasons.length === 0);
}

function render(view) {
  // Ignore anything older than what is already on screen.
  if (view.rev <= currentRev) return;
  currentRev = view.rev;
  currentView = view;

  if (view.kind) renderHeading(view);
  renderScanned(view);
  show(el.loading, view.status === "loading");
  show(el.result, view.status === "done");
  show(el.message, view.status === "error");
  show(el.retryBtn, view.status === "error" && RETRYABLE_CODES.has(view.errorCode));

  if (view.status === "done") {
    renderResult(view.result);
    show(el.moreNote, Boolean(view.content) && !canOpenWithInput(view.kind, view.content));
  } else if (view.status === "error") {
    el.message.textContent = errorMessage(view.errorCode);
    el.message.className = `message ${RETRYABLE_CODES.has(view.errorCode) ? "is-error" : "is-info"}`;
  }

  requestAnimationFrame(fitWindowToContent);
}

// Shrinks/grows the window to its content (cosmetic; safe to fail).
async function fitWindowToContent() {
  try {
    const win = await chrome.windows.getCurrent();
    const frameHeight = window.outerHeight - window.innerHeight;
    const contentHeight = Math.ceil(document.body.getBoundingClientRect().height);
    const wanted = Math.min(640, Math.max(240, contentHeight + frameHeight));
    if (Math.abs(wanted - win.height) > 4) await chrome.windows.update(win.id, { height: wanted });
  } catch {
    // ignore
  }
}

async function init() {
  show(el.demoBadge, demo);
  show(el.demoNote, demo);

  chrome.runtime.onMessage.addListener((message) => {
    if (message && message.type === "nexus:scan-update" && message.id === scanId) render(message.view);
  });

  // Opens the Nexus web app with the exact scanned URL / text, so it can show the full analysis.
  el.viewBtn.addEventListener("click", () => {
    if (currentView) openNexusWebApp(currentView.kind, currentView.content);
  });
  el.retryBtn.addEventListener("click", async () => {
    const view = await chrome.runtime.sendMessage({ type: "nexus:retry", id: scanId }).catch(() => null);
    render(view ?? { rev: currentRev + 1, status: "error", errorCode: "expired" });
  });

  const view = await chrome.runtime.sendMessage({ type: "nexus:get-scan", id: scanId }).catch(() => null);
  render(view ?? { rev: 1, status: "error", errorCode: "expired" });
}

init();
