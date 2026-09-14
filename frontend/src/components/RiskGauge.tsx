import { Info } from "lucide-react";

interface RiskGaugeProps {
  percent: number; // 0-100
  riskLabel: string; // "High risk" | "Medium risk" | "Low risk"
  color: string; // tailwind text/stroke color, e.g. "#ef4444"
}

export default function RiskGauge({ percent, riskLabel, color }: RiskGaugeProps) {
  const clamped = Math.max(0, Math.min(100, percent));

  return (
    <div className="flex flex-col items-center">
      <svg viewBox="0 0 200 115" className="w-full max-w-[190px]">
        <path
          d="M20,100 A80,80 0 0 1 180,100"
          fill="none"
          stroke="currentColor"
          className="text-slate-200 dark:text-white/10"
          strokeWidth={16}
          strokeLinecap="round"
        />
        <path
          d="M20,100 A80,80 0 0 1 180,100"
          fill="none"
          stroke={color}
          strokeWidth={16}
          strokeLinecap="round"
          pathLength={100}
          strokeDasharray={`${clamped} ${100 - clamped}`}
        />
        <text
          x="100"
          y="92"
          textAnchor="middle"
          className="fill-slate-900 dark:fill-white"
          fontSize="30"
          fontWeight="800"
        >
          {Math.round(clamped)}%
        </text>
      </svg>
      <p className="mt-1 flex items-center gap-1 text-sm font-semibold text-slate-700 dark:text-slate-200">
        Risk Score
        <Info size={13} className="text-slate-400" />
      </p>
      <p className="text-sm font-medium" style={{ color }}>
        {riskLabel}
      </p>
    </div>
  );
}
