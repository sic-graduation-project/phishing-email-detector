// Nexus extension configuration. These values live here and nowhere else.
//
// DEMO_MODE        true  = TEMPORARY UI testing mode. Results come from the
//                          built-in fake examples in demo-data.js and NO network
//                          request is made (no backend needed).
//                  false = real mode. Text and links are analyzed by the Nexus
//                          backend (POST /api/v1/analyze/text and /url).
// API_BASE_URL     The Nexus backend (same one the Nexus web app talks to).
//                  If you change it, ALSO change "host_permissions" in
//                  manifest.json to the same origin, or Chrome blocks the calls.
// NEXUS_APP_URL    The main Nexus web application, opened by "View Full Analysis".
//                  (http://localhost:5173 is where `npm run dev` serves it.)
// MAX_TEXT_LENGTH  Longest text selection that can be scanned. Same limit as the
//                  Nexus web app's text box.
// MAX_DEEP_LINK_LENGTH  Longest web address "View Full Analysis" may open (the
//                  scanned URL/text is encoded into it). Longer input opens the
//                  web app without it. Web servers reject very long addresses
//                  (Vite/Node: about 16,000; many servers: 8,000).
//
// After editing this file, reload the extension in chrome://extensions.
// Never put API keys or secrets in this file: anything inside an extension can
// be read by the user.
export const NEXUS_CONFIG = Object.freeze({
  // Production must use the real analyzer. Demo fixtures are opt-in only.
  DEMO_MODE: false,
  API_BASE_URL: "https://nexus-phishing-api.onrender.com",
  NEXUS_APP_URL: "https://nexus-phishing-detector.onrender.com",
  REQUEST_TIMEOUT_MS: 15000,
  MAX_TEXT_LENGTH: 5000,
  MAX_DEEP_LINK_LENGTH: 8000,
});
