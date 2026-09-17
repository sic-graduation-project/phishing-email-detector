import { useEffect, useMemo, useState } from "react";
import {
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
} from "recharts";
import { ScanLine, ShieldCheck, ShieldAlert, Percent, Trash2 } from "lucide-react";
import { Link } from "react-router-dom";
import { clearHistory, computeStats, getLocalHistory } from "../api/history";
import type { ScanResult } from "../types";
import StatCard from "../components/StatCard";
import VerdictBadge from "../components/VerdictBadge";
import ConfirmDialog from "../components/ConfirmDialog";

const PIE_COLORS: Record<string, string> = { Safe: "#10b981", Phishing: "#ef4444" };

export default function DashboardPage() {
  const [history, setHistory] = useState<ScanResult[]>([]);
  const [confirmClearOpen, setConfirmClearOpen] = useState(false);

  useEffect(() => {
    setHistory(getLocalHistory());
  }, []);

  const stats = useMemo(() => computeStats(history), [history]);

  function handleClear() {
    clearHistory();
    setHistory([]);
    setConfirmClearOpen(false);
  }

  const pieData = [
    { name: "Safe", value: stats.safeCount },
    { name: "Phishing", value: stats.phishingCount },
  ].filter((entry) => entry.value > 0);

  if (history.length === 0) {
    return (
      <div className="rounded-2xl border border-dashed border-slate-300 dark:border-white/15 p-12 text-center">
        <ScanLine size={32} className="mx-auto mb-4 text-slate-300 dark:text-slate-600" />
        <h2 className="text-lg font-semibold text-slate-700 dark:text-slate-200">
          No scans yet
        </h2>
        <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
          Run your first email scan to start building your detection history.
        </p>
        <Link
          to="/"
          className="mt-5 inline-flex rounded-xl bg-gradient-to-r from-blue-600 to-violet-600 px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-blue-600/25"
        >
          Scan an email
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-white">
            Analysis History
          </h1>
          <p className="mt-1 text-slate-500 dark:text-slate-400">
            Overview of every scan performed on this device.
          </p>
        </div>
        <button
          onClick={() => setConfirmClearOpen(true)}
          className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 dark:border-white/10 px-3 py-1.5 text-xs font-medium text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-white/10 transition-colors"
        >
          <Trash2 size={13} />
          Clear history
        </button>
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

      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard label="Total scans" value={String(stats.totalScans)} icon={ScanLine} tone="brand" />
        <StatCard label="Marked safe" value={String(stats.safeCount)} icon={ShieldCheck} tone="safe" />
        <StatCard label="Marked phishing" value={String(stats.phishingCount)} icon={ShieldAlert} tone="danger" />
        <StatCard
          label="Phishing rate"
          value={`${Math.round(stats.phishingRate * 100)}%`}
          icon={Percent}
          tone="slate"
        />
      </div>

      <div className="grid lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 rounded-2xl border border-slate-200/70 dark:border-white/10 bg-white dark:bg-white/5 p-5 shadow-sm">
          <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-200 mb-4">
            Scans over time
          </h3>
          <ResponsiveContainer width="100%" height={260}>
            <AreaChart data={stats.scansByDay}>
              <defs>
                <linearGradient id="safeGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#10b981" stopOpacity={0.35} />
                  <stop offset="100%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="phishGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#ef4444" stopOpacity={0.35} />
                  <stop offset="100%" stopColor="#ef4444" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" vertical={false} />
              <XAxis dataKey="date" tick={{ fontSize: 12, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
              <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: "#94a3b8" }} axisLine={false} tickLine={false} />
              <Tooltip
                contentStyle={{ borderRadius: 12, border: "1px solid #e2e8f0", fontSize: 13 }}
              />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Area type="monotone" dataKey="safe" name="Safe" stroke="#10b981" fill="url(#safeGrad)" strokeWidth={2} />
              <Area
                type="monotone"
                dataKey="phishing"
                name="Phishing"
                stroke="#ef4444"
                fill="url(#phishGrad)"
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        <div className="rounded-2xl border border-slate-200/70 dark:border-white/10 bg-white dark:bg-white/5 p-5 shadow-sm">
          <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-200 mb-4">
            Safe vs. Phishing
          </h3>
          <ResponsiveContainer width="100%" height={220}>
            <PieChart>
              <Pie
                data={pieData}
                dataKey="value"
                nameKey="name"
                innerRadius={55}
                outerRadius={80}
                paddingAngle={3}
              >
                {pieData.map((entry) => (
                  <Cell key={entry.name} fill={PIE_COLORS[entry.name]} />
                ))}
              </Pie>
              <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid #e2e8f0", fontSize: 13 }} />
              <Legend wrapperStyle={{ fontSize: 12 }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {stats.topReasons.length > 0 && (
        <div className="rounded-2xl border border-slate-200/70 dark:border-white/10 bg-white dark:bg-white/5 p-5 shadow-sm">
          <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-200 mb-4">
            Most common phishing indicators
          </h3>
          <ResponsiveContainer width="100%" height={Math.max(160, stats.topReasons.length * 42)}>
            <BarChart data={stats.topReasons} layout="vertical" margin={{ left: 8, right: 16 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" horizontal={false} />
              <XAxis type="number" allowDecimals={false} tick={{ fontSize: 12, fill: "#94a3b8" }} />
              <YAxis
                type="category"
                dataKey="reason"
                width={260}
                tick={{ fontSize: 12, fill: "#64748b" }}
              />
              <Tooltip contentStyle={{ borderRadius: 12, border: "1px solid #e2e8f0", fontSize: 13 }} />
              <Bar dataKey="count" fill="#6366f1" radius={[0, 6, 6, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      <div className="rounded-2xl border border-slate-200/70 dark:border-white/10 bg-white dark:bg-white/5 shadow-sm overflow-hidden">
        <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-200 px-5 pt-5 mb-2">
          Recent scans
        </h3>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs uppercase tracking-wide text-slate-400 border-b border-slate-100 dark:border-white/10">
                <th className="px-5 py-2 font-medium">When</th>
                <th className="px-5 py-2 font-medium">Subject</th>
                <th className="px-5 py-2 font-medium">Type</th>
                <th className="px-5 py-2 font-medium">Result</th>
              </tr>
            </thead>
            <tbody>
              {history.slice(0, 20).map((scan) => (
                <tr
                  key={scan.id}
                  className="border-b border-slate-50 dark:border-white/5 last:border-0"
                >
                  <td className="px-5 py-3 text-slate-400 whitespace-nowrap">
                    {new Date(scan.scannedAt).toLocaleString()}
                  </td>
                  <td className="px-5 py-3 text-slate-700 dark:text-slate-200 max-w-[260px] truncate">
                    {scan.subject || scan.snippet}
                  </td>
                  <td className="px-5 py-3 text-slate-500 dark:text-slate-400 max-w-[200px] truncate capitalize">
                    {scan.kind}
                  </td>
                  <td className="px-5 py-3">
                    <VerdictBadge verdict={scan.verdict} size="sm" />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
