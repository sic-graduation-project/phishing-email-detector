import { useEffect, useRef, useState } from "react";
import { Bell, ShieldAlert, ScanLine, Sparkles } from "lucide-react";

interface Notification {
  id: string;
  icon: typeof Bell;
  tone: "danger" | "brand" | "slate";
  title: string;
  time: string;
}

const NOTIFICATIONS: Notification[] = [
  {
    id: "1",
    icon: ShieldAlert,
    tone: "danger",
    title: "Phishing detected in your latest scan.",
    time: "2 minutes ago",
  },
  {
    id: "2",
    icon: ScanLine,
    tone: "brand",
    title: "Weekly summary: 4 scans completed, 1 flagged.",
    time: "1 day ago",
  },
  {
    id: "3",
    icon: Sparkles,
    tone: "slate",
    title: "Welcome to PhishGuard — start by scanning an email.",
    time: "3 days ago",
  },
];

const toneStyles: Record<string, string> = {
  danger: "bg-red-50 text-red-600 dark:bg-red-500/10 dark:text-red-400",
  brand: "bg-blue-50 text-blue-600 dark:bg-blue-500/10 dark:text-blue-400",
  slate: "bg-slate-100 text-slate-500 dark:bg-white/10 dark:text-slate-300",
};

export default function NotificationsDropdown() {
  const [open, setOpen] = useState(false);
  const [unread, setUnread] = useState(true);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    function handleClickOutside(e: MouseEvent) {
      if (containerRef.current && !containerRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    function handleEscape(e: KeyboardEvent) {
      if (e.key === "Escape") setOpen(false);
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
        onClick={() => {
          setOpen((o) => !o);
          setUnread(false);
        }}
        aria-label="Notifications"
        aria-expanded={open}
        className="relative grid place-items-center h-9 w-9 rounded-full text-slate-500 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/10 transition-colors"
      >
        <Bell size={18} />
        {unread && (
          <span className="absolute top-1.5 right-1.5 h-2 w-2 rounded-full bg-red-500 ring-2 ring-white dark:ring-[#0f1420]" />
        )}
      </button>

      {open && (
        <div className="absolute right-0 top-full mt-2 w-80 max-w-[90vw] rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-[#0f1420] shadow-xl shadow-slate-900/10 overflow-hidden z-40 animate-scale-in">
          <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100 dark:border-white/10">
            <p className="font-semibold text-sm text-slate-800 dark:text-slate-100">Notifications</p>
            <span className="text-xs text-slate-400">{NOTIFICATIONS.length} new</span>
          </div>
          <ul className="max-h-80 overflow-y-auto divide-y divide-slate-50 dark:divide-white/5">
            {NOTIFICATIONS.map(({ id, icon: Icon, tone, title, time }) => (
              <li key={id} className="flex items-start gap-3 px-4 py-3 hover:bg-slate-50 dark:hover:bg-white/5 transition-colors">
                <span className={`grid place-items-center h-8 w-8 shrink-0 rounded-full ${toneStyles[tone]}`}>
                  <Icon size={15} />
                </span>
                <div className="min-w-0">
                  <p className="text-sm text-slate-700 dark:text-slate-200 leading-snug">{title}</p>
                  <p className="mt-0.5 text-xs text-slate-400">{time}</p>
                </div>
              </li>
            ))}
          </ul>
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
