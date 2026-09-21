export type Verdict = "safe" | "phishing";
export type InputKind = "email" | "url" | "text";

export interface ScanRequest {
  kind: InputKind;
  subject?: string;
  body: string;
}

export interface ScanResult {
  id: string;
  kind: InputKind;
  verdict: Verdict;
  riskScore: number; // 0-100, as returned by the backend
  reasons: string[];
  scannedAt: string; // ISO date
  subject?: string;
  snippet: string;
}

export interface DashboardStats {
  totalScans: number;
  phishingCount: number;
  safeCount: number;
  phishingRate: number; // 0-1
  scansByDay: { date: string; safe: number; phishing: number }[];
  topReasons: { reason: string; count: number }[];
}
