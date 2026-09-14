import axios from "axios";
import type { InputKind, ScanRequest, ScanResult } from "../types";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

const http = axios.create({
  baseURL: API_BASE_URL,
  timeout: 8000,
});

const PHISHING_KEYWORDS = [
  "verify your account",
  "urgent",
  "click here",
  "suspended",
  "password expires",
  "confirm your identity",
  "wire transfer",
  "gift card",
  "act now",
  "limited time",
  "login immediately",
  "unusual activity",
  "otp",
  "one time password",
];

const SUSPICIOUS_TLDS = ["ru", "tk", "xyz", "zip", "top", "gq", "cf"];

function scoreEmail(request: ScanRequest) {
  const text = `${request.subject ?? ""} ${request.body}`.toLowerCase();
  const matched = PHISHING_KEYWORDS.filter((k) => text.includes(k));
  const hasSuspiciousLink = /https?:\/\/[^\s]*\.(ru|tk|xyz|zip)[^\s]*/i.test(request.body);
  const score = Math.min(1, matched.length * 0.2 + (hasSuspiciousLink ? 0.35 : 0));

  const reasons =
    score >= 0.4
      ? [
          ...matched.map((k) => `Uses urgent/social-engineering language: "${k}"`),
          ...(hasSuspiciousLink ? ["Contains suspicious links"] : []),
          ...(matched.some((k) => k.includes("password") || k.includes("otp"))
            ? ["Requests sensitive information (e.g. password, OTP)"]
            : []),
        ]
      : [];

  return { score, reasons };
}

function scoreUrl(request: ScanRequest) {
  const url = request.body.trim();
  let score = 0;
  const reasons: string[] = [];

  if (/^https?:\/\/\d{1,3}(\.\d{1,3}){3}/i.test(url)) {
    score += 0.4;
    reasons.push("Uses a raw IP address instead of a domain name");
  }
  const tldMatch = url.match(/\.([a-z]{2,10})(?:[/?#]|$)/i);
  if (tldMatch && SUSPICIOUS_TLDS.includes(tldMatch[1].toLowerCase())) {
    score += 0.3;
    reasons.push(`Uses an uncommon top-level domain (.${tldMatch[1]})`);
  }
  if ((url.match(/-/g) ?? []).length >= 3) {
    score += 0.15;
    reasons.push("Domain contains an unusual number of hyphens");
  }
  if (url.includes("@")) {
    score += 0.25;
    reasons.push("Contains an \"@\" symbol that can hide the real destination");
  }
  if (url.length > 90) {
    score += 0.15;
    reasons.push("Unusually long URL, often used to obscure the real link");
  }
  if (url.startsWith("http://")) {
    score += 0.1;
    reasons.push("Does not use a secure HTTPS connection");
  }

  return { score: Math.min(1, score), reasons };
}

function scoreText(request: ScanRequest) {
  const text = request.body.toLowerCase();
  const matched = PHISHING_KEYWORDS.filter((k) => text.includes(k));
  const score = Math.min(1, matched.length * 0.25);
  const reasons = matched.map((k) => `Contains urgent/social-engineering phrase: "${k}"`);
  return { score, reasons };
}

function demoScan(request: ScanRequest): ScanResult {
  const scorer = request.kind === "url" ? scoreUrl : request.kind === "text" ? scoreText : scoreEmail;
  const { score, reasons } = scorer(request);
  const verdict = score >= 0.4 ? "phishing" : "safe";

  const finalReasons = verdict === "phishing"
    ? reasons.length
      ? reasons
      : ["Matches known phishing patterns"]
    : ["No known phishing indicators detected in this demo heuristic"];

  return {
    id: crypto.randomUUID(),
    kind: request.kind,
    verdict,
    confidence: verdict === "phishing" ? Math.max(score, 0.55) : Math.max(1 - score, 0.6),
    reasons: finalReasons,
    scannedAt: new Date().toISOString(),
    subject: request.subject,
    sender: request.sender,
    snippet: request.body.slice(0, 140),
    source: "demo",
  };
}

export type ForceVerdict = "auto" | "phishing" | "safe";

const FORCED_PHISHING_REASONS = [
  "Uses urgent language (e.g. account suspension)",
  "Contains suspicious links",
  "Requests sensitive information (e.g. password, OTP)",
  "Matches known phishing patterns",
  "Possible brand impersonation detected",
];

const FORCED_SAFE_REASONS = [
  "No urgent or threatening language detected",
  "No suspicious links found",
  "Does not request sensitive information",
  "Does not match known phishing patterns",
];

function applyForceOverride(result: ScanResult, force: ForceVerdict): ScanResult {
  if (force === "auto") return result;
  const verdict = force;
  return {
    ...result,
    verdict,
    confidence: verdict === "phishing" ? 0.94 : 0.95,
    reasons: verdict === "phishing" ? FORCED_PHISHING_REASONS : FORCED_SAFE_REASONS,
    source: "demo",
  };
}

export async function scanEmail(request: ScanRequest, force: ForceVerdict = "auto"): Promise<ScanResult> {
  let result: ScanResult;
  try {
    const { data } = await http.post<ScanResult>("/api/scan", request);
    result = { ...data, source: "api" };
  } catch {
    await new Promise((r) => setTimeout(r, 700));
    result = demoScan(request);
  }
  return applyForceOverride(result, force);
}

export async function fetchRemoteHistory(): Promise<ScanResult[] | null> {
  try {
    const { data } = await http.get<ScanResult[]>("/api/history");
    return data;
  } catch {
    return null;
  }
}

export const inputKindLabel: Record<InputKind, string> = {
  email: "Email",
  url: "URL",
  text: "Text",
};
