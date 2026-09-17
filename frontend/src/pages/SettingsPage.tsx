import { useState } from "react";
import { Settings as SettingsIcon, Moon, Bell, Trash2 } from "lucide-react";
import { useTheme } from "../hooks/useTheme";
import { clearHistory } from "../api/history";
import ConfirmDialog from "../components/ConfirmDialog";

export default function SettingsPage() {
  const { theme, toggleTheme } = useTheme();
  const [confirmClearOpen, setConfirmClearOpen] = useState(false);

  function handleClear() {
    clearHistory();
    setConfirmClearOpen(false);
  }

  return (
    <div className="max-w-2xl">
      <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
        Settings
      </h1>
      <p className="mt-1.5 text-slate-500 dark:text-slate-400">
        Manage your PhishGuard preferences.
      </p>

      <div className="mt-6 rounded-2xl border border-slate-200 dark:border-white/10 bg-white dark:bg-white/5 divide-y divide-slate-100 dark:divide-white/10">
        <div className="flex items-center justify-between p-5">
          <div className="flex items-center gap-3">
            <div className="grid place-items-center h-10 w-10 rounded-xl bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400">
              <Moon size={18} />
            </div>
            <div>
              <p className="font-medium text-slate-800 dark:text-slate-100">Dark mode</p>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                Switch between light and dark appearance.
              </p>
            </div>
          </div>
          <button
            onClick={toggleTheme}
            className={`relative h-6 w-11 rounded-full transition-colors ${
              theme === "dark" ? "bg-blue-600" : "bg-slate-300"
            }`}
          >
            <span
              className={`absolute top-0.5 h-5 w-5 rounded-full bg-white transition-transform ${
                theme === "dark" ? "translate-x-5" : "translate-x-0.5"
              }`}
            />
          </button>
        </div>

        <div className="flex items-center justify-between p-5">
          <div className="flex items-center gap-3">
            <div className="grid place-items-center h-10 w-10 rounded-xl bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400">
              <Bell size={18} />
            </div>
            <div>
              <p className="font-medium text-slate-800 dark:text-slate-100">Notifications</p>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                Get notified when a scan finishes.
              </p>
            </div>
          </div>
          <button className="relative h-6 w-11 rounded-full bg-blue-600">
            <span className="absolute top-0.5 translate-x-5 h-5 w-5 rounded-full bg-white" />
          </button>
        </div>

        <div className="flex items-center justify-between p-5">
          <div className="flex items-center gap-3">
            <div className="grid place-items-center h-10 w-10 rounded-xl bg-red-50 dark:bg-red-500/10 text-red-600 dark:text-red-400">
              <Trash2 size={18} />
            </div>
            <div>
              <p className="font-medium text-slate-800 dark:text-slate-100">Clear scan history</p>
              <p className="text-sm text-slate-500 dark:text-slate-400">
                Removes all locally stored analysis results.
              </p>
            </div>
          </div>
          <button
            onClick={() => setConfirmClearOpen(true)}
            className="rounded-lg border border-red-200 dark:border-red-500/20 px-3 py-1.5 text-sm font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-500/10 transition-colors"
          >
            Clear
          </button>
        </div>
      </div>

      <ConfirmDialog
        open={confirmClearOpen}
        title="Clear scan history?"
        message="Are you sure you want to delete all scan history? This action cannot be undone."
        confirmLabel="Delete"
        cancelLabel="Cancel"
        onConfirm={handleClear}
        onCancel={() => setConfirmClearOpen(false)}
      />

      <p className="mt-6 flex items-center gap-2 text-xs text-slate-400">
        <SettingsIcon size={13} />
        More configuration options will appear here as PhishGuard grows.
      </p>
    </div>
  );
}
