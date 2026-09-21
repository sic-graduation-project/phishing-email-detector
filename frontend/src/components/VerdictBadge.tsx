import { ShieldCheck, ShieldAlert } from "lucide-react";
import type { Verdict } from "../types";

export default function VerdictBadge({ verdict, size = "md" }: { verdict: Verdict; size?: "sm" | "md" }) {
  const isSafe = verdict === "safe";
  const sizeClasses = size === "md" ? "px-4 py-2 text-base gap-2" : "px-2.5 py-1 text-xs gap-1";
  const iconSize = size === "md" ? 20 : 14;

  return (
    <span
      className={`inline-flex items-center rounded-full font-semibold ${sizeClasses} ${
        isSafe
          ? "bg-emerald-50 text-emerald-600 dark:bg-emerald-500/10 dark:text-emerald-400"
          : "bg-red-50 text-red-600 dark:bg-red-500/10 dark:text-red-400"
      }`}
    >
      {isSafe ? <ShieldCheck size={iconSize} /> : <ShieldAlert size={iconSize} />}
      {isSafe ? "Safe" : "Phishing"}
    </span>
  );
}
