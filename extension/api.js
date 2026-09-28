// Shared helpers for talking to the Nexus backend.
//
// Nothing here decides whether content is phishing. The classification, risk
// score and reasons are whatever the backend returns; this file only sends the
// request and checks that the response has the expected shape.
import { NEXUS_CONFIG } from "./config.js";
import { DEMO_DELAY_MS, getDemoResponse } from "./demo-data.js";

export class ScanError extends Error {
  constructor(code) {
    super(code);
    this.code = code;
  }
}

// Same endpoints and request bodies as the Nexus web app (frontend/src/api/client.ts).
const ENDPOINTS = {
  text: "/api/v1/analyze/text",
  url: "/api/v1/analyze/url",
};

const MESSAGES = {
  emptySelection: "No text is selected. Select some text and try again.",
  unsupportedPage: "Nexus can only scan text selected on regular web pages (http or https).",
  unsupportedLink: "This link cannot be scanned. Nexus supports http and https links only.",
  offline: "Unable to connect to the Nexus analysis service.",
  timeout: "The Nexus analysis service took too long to respond. Please try again.",
  serverError: "The Nexus analysis service returned an error. Please try again later.",
  rejected: "The Nexus analysis service could not process this content.",
  invalidResponse: "The Nexus analysis service returned an unexpected response.",
  expired: "This scan is no longer available. Right-click again to start a new scan.",
  unknown: "Something went wrong while scanning. Please try again.",
  demoError: "Unable to analyze this input.", // DEMO MODE only: triggered by the demo error input
};

// Errors that may go away if the user simply tries again.
export const RETRYABLE_CODES = new Set(["offline", "timeout", "serverError", "invalidResponse", "unknown", "demoError"]);

export function errorMessage(code) {
  if (code === "textTooLong") {
    return `The selected text is too long to scan (maximum ${NEXUS_CONFIG.MAX_TEXT_LENGTH.toLocaleString()} characters). Please select a shorter passage.`;
  }
  return MESSAGES[code] ?? MESSAGES.unknown;
}

// The backend only accepts http(s) URLs.
export function isWebUrl(value) {
  try {
    const { protocol } = new URL(value);
    return protocol === "http:" || protocol === "https:";
  } catch {
    return false;
  }
}

function networkErrorCode(err) {
  return err && err.name === "TimeoutError" ? "timeout" : "offline";
}

// kind: "text" | "url". Resolves to { classification, riskScore, reasons } or throws ScanError.
export async function analyzeContent(kind, content) {
  const endpoint = ENDPOINTS[kind];
  if (!endpoint) throw new ScanError("unknown");
  const payload = kind === "text" ? { text: content } : { url: content };

  let response;
  try {
    response = await fetch(`${NEXUS_CONFIG.API_BASE_URL}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(payload),
      credentials: "omit",
      cache: "no-store",
      signal: AbortSignal.timeout(NEXUS_CONFIG.REQUEST_TIMEOUT_MS),
    });
  } catch (err) {
    throw new ScanError(networkErrorCode(err));
  }

  if (response.status >= 400 && response.status < 500) throw new ScanError("rejected");
  if (!response.ok) throw new ScanError("serverError");

  let data;
  try {
    data = await response.json();
  } catch (err) {
    throw new ScanError(err && err.name === "TimeoutError" ? "timeout" : "invalidResponse");
  }
  return parseAnalysis(data);
}

// Fail closed on malformed backend data instead of rendering an unknown verdict
// with safe-looking styling.
function parseAnalysis(data) {
  if (!data || typeof data !== "object") throw new ScanError("invalidResponse");

  const { classification, risk_score: riskScore, reasons } = data;
  if (classification !== "Phishing" && classification !== "Legitimate") {
    throw new ScanError("invalidResponse");
  }
  if (!Number.isFinite(riskScore) || riskScore < 0 || riskScore > 100 || !Array.isArray(reasons)) {
    throw new ScanError("invalidResponse");
  }

  return {
    classification: classification.trim(),
    riskScore,
    reasons: reasons.filter((reason) => typeof reason === "string" && reason.trim() !== ""),
  };
}

// ---- Demo mode / real mode switch --------------------------------------------
// This is the ONLY place that reads NEXUS_CONFIG.DEMO_MODE to pick a data source:
//   DEMO_MODE = true  -> fake fixtures from demo-data.js, no network request
//   DEMO_MODE = false -> the real Nexus backend (analyzeContent above)
// Both return the same shape: { classification, riskScore, reasons }.

async function analyzeWithDemoData(kind, content) {
  await new Promise((resolve) => setTimeout(resolve, DEMO_DELAY_MS));
  const response = getDemoResponse(kind, content);
  if (response.errorCode) throw new ScanError(response.errorCode);
  return response.result;
}

function analyze(kind, content) {
  return NEXUS_CONFIG.DEMO_MODE ? analyzeWithDemoData(kind, content) : analyzeContent(kind, content);
}

export function analyzeText(text) {
  return analyze("text", text);
}

export function analyzeUrl(url) {
  return analyze("url", url);
}

// Lets the UI label demo results as demo results.
export function isDemoMode() {
  return NEXUS_CONFIG.DEMO_MODE === true;
}

// For the toolbar popup. In demo mode this makes no network request.
export async function getExtensionStatus() {
  if (isDemoMode()) return { mode: "demo" };
  return { mode: "api", backendOnline: await checkBackendHealth() };
}

// Real mode only: whether the backend is reachable.
async function checkBackendHealth() {
  try {
    const response = await fetch(`${NEXUS_CONFIG.API_BASE_URL}/api/v1/health`, {
      credentials: "omit",
      cache: "no-store",
      signal: AbortSignal.timeout(5000),
    });
    return response.ok;
  } catch {
    return false;
  }
}

// Address of the Nexus web app. With a scanned input it becomes a deep link the
// web app understands:  <app>/?url=<scanned URL>   or   <app>/?text=<scanned text>
// The value is percent-encoded, so any characters (&, #, %, spaces, quotes,
// non-Latin text...) reach the web app exactly as scanned.
// If the address would be longer than MAX_DEEP_LINK_LENGTH (servers reject very
// long addresses), the plain home page is used instead; see canOpenWithInput().
function deepLinkFor(kind, content) {
  const appUrl = new URL(NEXUS_CONFIG.NEXUS_APP_URL);
  appUrl.search = `?${kind}=${encodeURIComponent(content)}`;
  return appUrl.href;
}

function hasInput(kind, content) {
  return (kind === "url" || kind === "text") && typeof content === "string" && content !== "";
}

// Whether this scanned input can be handed to the web app in its address.
export function canOpenWithInput(kind, content) {
  return hasInput(kind, content) && deepLinkFor(kind, content).length <= NEXUS_CONFIG.MAX_DEEP_LINK_LENGTH;
}

export function buildNexusAppUrl(kind, content) {
  return canOpenWithInput(kind, content) ? deepLinkFor(kind, content) : new URL(NEXUS_CONFIG.NEXUS_APP_URL).href;
}

// Opens the main Nexus web application, optionally with the scanned input so the
// web app can show the full analysis. Called without arguments it opens the home page.
export function openNexusWebApp(kind, content) {
  if (!isWebUrl(NEXUS_CONFIG.NEXUS_APP_URL)) return;
  chrome.tabs.create({ url: buildNexusAppUrl(kind, content) });
}
