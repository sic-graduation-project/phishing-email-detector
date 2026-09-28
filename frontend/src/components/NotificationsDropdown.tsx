import { useCallback, useEffect, useRef, useState } from "react";
import { Bell, ShieldAlert } from "lucide-react";
import { getLocalHistory, getNotificationsEnabled, HISTORY_CHANGED_EVENT, NOTIFICATIONS_CHANGED_EVENT } from "../api/history";
import type { ScanResult } from "../types";

const LAST_READ_KEY = "phishguard.notifications_last_read";
const MAX_NOTIFICATIONS = 20;

function getNotifications(): ScanResult[] {
  if (!getNotificationsEnabled()) return [];
  return getLocalHistory()
    .filter((scan) => scan.verdict === "phishing")
    .slice(0, MAX_NOTIFICATIONS);
}

function getLastRead(): number {
  const value = Number(localStorage.getItem(LAST_READ_KEY));
  return Number.isFinite(value) ? value : 0;
}

function relativeTime(date: string): string {
  const elapsedSeconds = Math.max(0, Math.floor((Date.now() - new Date(date).getTime()) / 1000));
  if (elapsedSeconds < 60) return "Just now";
  const minutes = Math.floor(elapsedSeconds / 60);
  if (minutes < 60) return `${minutes} minute${minutes === 1 ? "" : "s"} ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} hour${hours === 1 ? "" : "s"} ago`;
  const days = Math.floor(hours / 24);
  return `${days} day${days === 1 ? "" : "s"} ago`;
}

export default function NotificationsDropdown() {
  const [open, setOpen] = useState(false);
  const [notifications, setNotifications] = useState<ScanResult[]>(getNotifications);
  const [lastRead, setLastRead] = useState(getLastRead);
  const containerRef = useRef<HTMLDivElement>(null);

  const refresh = useCallback(() => setNotifications(getNotifications()), []);
  const unreadCount = notifications.filter(
    (notification) => new Date(notification.scannedAt).getTime() > lastRead,
  ).length;

  function markAllRead(): void {
    const readAt = Date.now();
    try {
      localStorage.setItem(LAST_READ_KEY, String(readAt));
    } catch {
      // Reading still works when storage is unavailable; it simply will not persist.
    }
    setLastRead(readAt);
  }

  function toggleOpen(): void {
    setOpen((current) => {
      const next = !current;
      if (next && unreadCount > 0) markAllRead();
      return next;
    });
  }

  useEffect(() => {
    function handleStorage(event: StorageEvent) {
      if (event.key === "phishguard.scan_history") refresh();
      if (event.key === LAST_READ_KEY) setLastRead(getLastRead());
    }
    window.addEventListener(HISTORY_CHANGED_EVENT, refresh);
    window.addEventListener(NOTIFICATIONS_CHANGED_EVENT, refresh);
    window.addEventListener("storage", handleStorage);
    return () => {
      window.removeEventListener(HISTORY_CHANGED_EVENT, refresh);
      window.removeEventListener(NOTIFICATIONS_CHANGED_EVENT, refresh);
      window.removeEventListener("storage", handleStorage);
    };
  }, [refresh]);

  useEffect(() => {
    if (!open) return;
    function handleClickOutside(event: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    function handleEscape(event: KeyboardEvent) {
      if (event.key === "Escape") setOpen(false);
    }
    document.addEventListener("mousedown", handleClickOutside);
    document.addEventListener("keydown", handleEscape);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
      document.removeEventListener("keydown", handleEscape);
    };
  }, [open]);

  return (
    <div className="relative" ref={containerRef}>
      <button
        onClick={toggleOpen}
        aria-label={unreadCount ? `Notifications, ${unreadCount} unread` : "Notifications"}
        aria-expanded={open}
        className="relative grid place-items-center h-9 w-9 rounded-full text-slate-500 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/10 transition-colors"
      >
        <Bell size={18} />
        {unreadCount > 0 && (
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-red-500 ring-2 ring-white dark:ring-[#0f1420]" />
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-2 w-80 max-w-[90vw] rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-[#0f1420] shadow-xl shadow-slate-900/10 overflow-hidden z-40 animate-scale-in">
          <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100 dark:border-white/10">
            <p className="font-semibold text-sm text-slate-800 dark:text-slate-100">Notifications</p>
            {unreadCount > 0 && <span className="text-xs text-slate-400">{unreadCount} new</span>}
          </div>

          {notifications.length === 0 ? (
            <div className="px-5 py-8 text-center">
              <Bell size={22} className="mx-auto text-slate-300 dark:text-slate-600" />
              <p className="mt-2 text-sm font-medium text-slate-600 dark:text-slate-300">
                No notifications
              </p>
              <p className="mt-1 text-xs text-slate-400">
                Phishing alerts from your scans will appear here.
              </p>
            </div>
          ) : (
            <ul className="max-h-80 overflow-y-auto divide-y divide-slate-50 dark:divide-white/5">
              {notifications.map((notification) => (
                <li key={notification.id} className="flex items-start gap-3 px-4 py-3 hover:bg-slate-50 dark:hover:bg-white/5 transition-colors">
                  <span className="grid place-items-center h-8 w-8 shrink-0 rounded-full bg-red-50 text-red-600 dark:bg-red-500/10 dark:text-red-400">
                    <ShieldAlert size={15} />
                  </span>
                  <div className="min-w-0">
                    <p className="text-sm text-slate-700 dark:text-slate-200 leading-snug">
                      Phishing detected in your {notification.kind} scan.
                    </p>
                    <p className="mt-0.5 text-xs text-slate-400">
                      {relativeTime(notification.scannedAt)} · {Math.round(notification.riskScore)}% risk
                    </p>
                  </div>
                </li>
              ))}
            </ul>
          )}

          <button
            onClick={() => setOpen(false)}
            className="w-full py-2.5 text-center text-xs font-medium text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-500/10 transition-colors border-t border-slate-100 dark:border-white/10"
          >
            Close
          </button>
        </div>
      )}
    </div>
  );
}
