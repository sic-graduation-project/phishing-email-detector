// DEMO MODE fixtures. FAKE results for UI testing only.
//
// This is NOT a phishing detector and never makes a network request. It is a
// lookup table: if the input is exactly one of the predefined demo test values
// below, the matching pre-written result is returned. Every other input gets the
// same generic demo result. Nothing here inspects or scores the content.
//
// All demo values are clearly fictional (.test domains are reserved and never
// resolve to real sites).

export const DEMO_DELAY_MS = 800; // simulated "analyzing" time so the loading UI can be tested

const NO_INDICATORS = ["No major phishing indicators detected."];

const PHISHING_TEXT = {
  classification: "Phishing",
  riskScore: 87,
  reasons: ["Urgency language detected", "Request for account verification", "Suspicious call to action"],
};
const LEGITIMATE_TEXT = { classification: "Legitimate", riskScore: 5, reasons: NO_INDICATORS };
const PHISHING_URL = {
  classification: "Phishing",
  riskScore: 92,
  reasons: ["Suspicious domain", "Suspicious URL structure", "Login-related path"],
};
const LEGITIMATE_URL = { classification: "Legitimate", riskScore: 5, reasons: NO_INDICATORS };
const GENERIC = {
  classification: "Demo Result",
  riskScore: null,
  reasons: [
    "This input is not one of the predefined demo test values, so this is a generic demo result.",
    "See the Demo Mode section of the extension README for inputs that show Phishing, Legitimate and error results.",
  ],
};
const DEMO_ERROR = { errorCode: "demoError" };

// Compared after trimming, collapsing whitespace and ignoring case.
const normalizeText = (text) => text.trim().replace(/\s+/g, " ").toLowerCase();

const TEXT_FIXTURES = new Map([
  [normalizeText("Your account has been suspended. Click here immediately to verify your account."), PHISHING_TEXT],
  [normalizeText("Your account has been suspended. Please verify your account immediately."), PHISHING_TEXT],
  [normalizeText("Welcome to our official website. Learn more about our services."), LEGITIMATE_TEXT],
  [normalizeText("Welcome to our website. Learn more about our services."), LEGITIMATE_TEXT],
  [normalizeText("DEMO_ERROR"), DEMO_ERROR],
]);

// Links are matched by their host name, so any path on a demo host works.
const URL_FIXTURES = new Map([
  ["demo-phishing.test", PHISHING_URL],
  ["example-phishing.test", PHISHING_URL],
  ["demo-safe.test", LEGITIMATE_URL],
  ["demo-error.test", DEMO_ERROR],
]);

function hostOf(url) {
  try {
    return new URL(url).hostname.toLowerCase();
  } catch {
    return "";
  }
}

// kind: "text" | "url". Returns { result } or { errorCode }.
export function getDemoResponse(kind, content) {
  const fixtures = kind === "url" ? URL_FIXTURES : TEXT_FIXTURES;
  const key = kind === "url" ? hostOf(content) : normalizeText(content);
  const fixture = fixtures.get(key) ?? GENERIC;

  if (fixture.errorCode) return { errorCode: fixture.errorCode };
  return { result: { ...fixture, reasons: [...fixture.reasons] } };
}
