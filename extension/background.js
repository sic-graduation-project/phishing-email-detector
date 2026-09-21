// Nexus service worker.
//
// Right-click flows:
//   selected text -> "Scan Text with Nexus" -> POST /api/v1/analyze/text
//   a link        -> "Scan URL with Nexus"  -> POST /api/v1/analyze/url
//
// The worker only forwards what the user explicitly chose (info.selectionText or
// info.linkUrl) to the Nexus backend and shows the backend's answer in a small
// result window (result.html). It never classifies anything itself.
import { NEXUS_CONFIG } from "./config.js";
import { analyzeText, analyzeUrl, isDemoMode, ScanError, isWebUrl } from "./api.js";

const MENU_SCAN_TEXT = "nexus-scan-text";
const MENU_SCAN_URL = "nexus-scan-url";

const RESULT_WINDOW = { width: 400, height: 560 };
const MAX_KEPT_SCANS = 20;
const PREVIEW_LENGTH = 200;

// In-memory only: scans exist while their result window is open and are never
// written to storage. (If Chrome stops the worker, they are simply gone.)
const scans = new Map();

// Makes demo mode obvious on the toolbar icon (runs every time the worker starts).
chrome.action.setBadgeText({ text: isDemoMode() ? "DEMO" : "" });
chrome.action.setBadgeBackgroundColor({ color: "#b45309" });

chrome.runtime.onInstalled.addListener(() => {
  chrome.contextMenus.removeAll(() => {
    chrome.contextMenus.create({ id: MENU_SCAN_TEXT, title: "Scan Text with Nexus", contexts: ["selection"] });
    chrome.contextMenus.create({ id: MENU_SCAN_URL, title: "Scan URL with Nexus", contexts: ["link"] });
  });
});

chrome.contextMenus.onClicked.addListener((info) => {
  if (info.menuItemId === MENU_SCAN_TEXT) startScan(prepareTextScan(info));
  else if (info.menuItemId === MENU_SCAN_URL) startScan(prepareUrlScan(info));
});

// ---- Validation: decide what (if anything) may be sent ----------------------

function prepareTextScan(info) {
  const text = (info.selectionText || "").trim();
  const base = { kind: "text", content: text, preview: previewOf(text) };

  if (!isWebUrl(info.pageUrl)) return { ...base, errorCode: "unsupportedPage" };
  if (!text) return { ...base, errorCode: "emptySelection" };
  if (text.length > NEXUS_CONFIG.MAX_TEXT_LENGTH) return { ...base, errorCode: "textTooLong" };
  return base;
}

// Scans the link that was right-clicked, never the URL of the current page.
function prepareUrlScan(info) {
  const url = info.linkUrl || "";
  const base = { kind: "url", content: url, preview: url };

  if (!isWebUrl(url)) return { ...base, errorCode: "unsupportedLink" };
  return base;
}

function previewOf(text) {
  const oneLine = text.replace(/\s+/g, " ");
  return oneLine.length > PREVIEW_LENGTH ? `${oneLine.slice(0, PREVIEW_LENGTH)}…` : oneLine;
}

// ---- Scan lifecycle ---------------------------------------------------------

function startScan(prepared) {
  const state = {
    id: crypto.randomUUID(),
    rev: 1,
    kind: prepared.kind,
    content: prepared.content,
    preview: prepared.preview,
    status: "loading",
    result: null,
    errorCode: null,
    windowId: null,
  };

  if (scans.size >= MAX_KEPT_SCANS) scans.delete(scans.keys().next().value);
  scans.set(state.id, state);

  if (prepared.errorCode) {
    state.status = "error";
    state.errorCode = prepared.errorCode;
    state.content = ""; // nothing will be sent, so nothing needs to be kept
  }

  openResultWindow(state);
  if (state.status === "loading") runScan(state);
}

async function runScan(state) {
  state.status = "loading";
  state.result = null;
  state.errorCode = null;
  state.rev += 1;
  publish(state);

  try {
    // Demo data or the real backend, depending on DEMO_MODE (decided in api.js).
    state.result = await (state.kind === "url" ? analyzeUrl(state.content) : analyzeText(state.content));
    state.status = "done";
  } catch (err) {
    state.status = "error";
    state.errorCode = err instanceof ScanError ? err.code : "unknown";
  }
  state.rev += 1;
  publish(state);
}

// What the result window gets. It includes the exact scanned content so that
// "View Full Analysis" can hand it to the Nexus web app even after Chrome has
// stopped this worker (the window keeps it in its own memory, never in storage).
function toView(state) {
  return {
    rev: state.rev,
    kind: state.kind,
    content: state.content,
    preview: state.preview,
    status: state.status,
    result: state.result,
    errorCode: state.errorCode,
  };
}

function publish(state) {
  // Fails harmlessly when the result window is not open (yet).
  chrome.runtime.sendMessage({ type: "nexus:scan-update", id: state.id, view: toView(state) }).catch(() => {});
}

// ---- Result window ----------------------------------------------------------

async function openResultWindow(state) {
  try {
    const win = await chrome.windows.create({
      url: `result.html?id=${state.id}`,
      type: "popup",
      focused: true,
      ...RESULT_WINDOW,
      ...(await positionNearBrowserWindow()),
    });
    state.windowId = win.id;
  } catch (err) {
    console.error("Nexus: could not open the result window", err);
    scans.delete(state.id);
  }
}

// Places the result window at the top right of the browser window the user is in.
async function positionNearBrowserWindow() {
  try {
    const current = await chrome.windows.getLastFocused();
    if (current.width && current.left !== undefined) {
      return {
        left: Math.max(0, current.left + current.width - RESULT_WINDOW.width - 24),
        top: Math.max(0, (current.top ?? 0) + 72),
      };
    }
  } catch {
    // fall back to Chrome's default placement
  }
  return {};
}

chrome.windows.onRemoved.addListener((windowId) => {
  for (const [id, state] of scans) {
    if (state.windowId === windowId) scans.delete(id);
  }
});

// The result window asks for its scan's current state, and can ask for a retry.
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (sender.id !== chrome.runtime.id || !message) return;

  const state = scans.get(message.id);
  if (message.type === "nexus:get-scan") {
    sendResponse(state ? toView(state) : null);
  } else if (message.type === "nexus:retry") {
    if (state && state.content) runScan(state);
    sendResponse(state ? toView(state) : null);
  }
});
