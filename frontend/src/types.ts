export type Verdict = "safe" | "phishing";
export type InputKind = "email" | "url" | "text";

export interface ScanRequest {
  kind: InputKind;
  subject?: string;
  sender?: string;
  body: string;
}

export interface ScanResult {
  id: string;
  kind: InputKind;
  verdict: Verdict;
  confidence: number; // 0-1, confidence in the verdict
  reasons: string[];
  scannedAt: string; // ISO date
  subject?: string;
  sender?: string;
  snippet: string;
  source: "api" | "demo";
}

export interface DashboardStats {
  totalScans: number;
  phishingCount: number;
  safeCount: number;
  phishingRate: number; // 0-1
  scansByDay: { date: string; safe: number; phishing: number }[];
  topReasons: { reason: string; count: number }[];
}
