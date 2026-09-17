/*
مسؤول عن:

حفظ نتائج الفحوصات في localStorage.
جلب نتائج الفحوصات السابقة.
حذف سجل الفحوصات.
حساب إحصائيات Dashboard.
*/
import type { DashboardStats, ScanResult } from "../types";

const STORAGE_KEY = "phishguard.scan_history";
const MAX_HISTORY = 200;

export function getLocalHistory(): ScanResult[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as ScanResult[]) : [];
  } catch {
    return [];
  }
}

export function saveScanToHistory(result: ScanResult): ScanResult[] {
  const history = [result, ...getLocalHistory()].slice(0, MAX_HISTORY);
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(history));
  } catch {
    // storage unavailable (private browsing, quota) — history just won't persist
  }
  return history;
}

export function clearHistory(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    // ignore
  }
}

export function computeStats(history: ScanResult[]): DashboardStats {
  const totalScans = history.length;
  const phishingCount = history.filter((h) => h.verdict === "phishing").length;
  const safeCount = totalScans - phishingCount;

  const byDay = new Map<string, { safe: number; phishing: number }>();
  for (const scan of history) {
    const date = scan.scannedAt.slice(0, 10);
    const entry = byDay.get(date) ?? { safe: 0, phishing: 0 };
    if (scan.verdict === "phishing") entry.phishing += 1;
    else entry.safe += 1;
    byDay.set(date, entry);
  }
  const scansByDay = Array.from(byDay.entries())
    .map(([date, counts]) => ({ date, ...counts }))
    .sort((a, b) => a.date.localeCompare(b.date))
    .slice(-14);

  const reasonCounts = new Map<string, number>();
  for (const scan of history) {
    if (scan.verdict !== "phishing") continue;
    for (const reason of scan.reasons) {
      reasonCounts.set(reason, (reasonCounts.get(reason) ?? 0) + 1);
    }
  }
  const topReasons = Array.from(reasonCounts.entries())
    .map(([reason, count]) => ({ reason, count }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 5);

  return {
    totalScans,
    phishingCount,
    safeCount,
    phishingRate: totalScans ? phishingCount / totalScans : 0,
    scansByDay,
    topReasons,
  };
}
