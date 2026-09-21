import type { LucideIcon } from "lucide-react";

interface StatCardProps {
  label: string;
  value: string;
  icon: LucideIcon;
  tone?: "brand" | "safe" | "danger" | "slate";
}

const toneStyles: Record<string, string> = {
  brand: "bg-blue-50 text-blue-600 dark:bg-blue-500/10 dark:text-blue-400",
  safe: "bg-emerald-50 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-400",
  danger: "bg-red-50 text-red-600 dark:bg-red-500/10 dark:text-red-400",
  slate: "bg-slate-100 text-slate-600 dark:bg-white/10 dark:text-slate-300",
};

export default function StatCard({ label, value, icon: Icon, tone = "slate" }: StatCardProps) {
  return (
    <div className="rounded-2xl border border-slate-200/70 dark:border-white/10 bg-white dark:bg-white/5 p-5 shadow-sm animate-fade-up">
      <div className={`inline-flex h-10 w-10 items-center justify-center rounded-xl ${toneStyles[tone]}`}>
        <Icon size={20} />
      </div>
      <p className="mt-3 text-2xl font-bold text-slate-900 dark:text-white">{value}</p>
      <p className="text-sm text-slate-500 dark:text-slate-400">{label}</p>
    </div>
  );
}
