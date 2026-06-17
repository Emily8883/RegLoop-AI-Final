"use client";

import type { PriorityBreakdown } from "@/types";
import { PRIORITY_CONFIG } from "@/constants/config";

interface PriorityChartProps {
  data: PriorityBreakdown | null | undefined;
  isLoading?: boolean;
}

export function PriorityChart({ data, isLoading }: PriorityChartProps) {
  if (isLoading) {
    return <div className="h-40 w-full animate-pulse rounded-[22px] bg-slate-100" />;
  }

  const breakdown = data || {
    high: 0,
    medium: 0,
    low: 0,
    high_coverage: 0,
    medium_coverage: 0,
    low_coverage: 0,
  };

  const total = (breakdown.high ?? 0) + (breakdown.medium ?? 0) + (breakdown.low ?? 0);

  if (total === 0) {
    return <div className="py-8 text-center text-slate-500">No priority data available</div>;
  }

  const bars = [
    {
      label: "High Priority",
      value: breakdown.high ?? 0,
      key: "high",
      color: PRIORITY_CONFIG.high.color,
      coverage: breakdown.high_coverage ?? 0,
    },
    {
      label: "Medium Priority",
      value: breakdown.medium ?? 0,
      key: "medium",
      color: PRIORITY_CONFIG.medium.color,
      coverage: breakdown.medium_coverage ?? 0,
    },
    {
      label: "Low Priority",
      value: breakdown.low ?? 0,
      key: "low",
      color: PRIORITY_CONFIG.low.color,
      coverage: breakdown.low_coverage ?? 0,
    },
  ];

  return (
    <div className="space-y-5">
      {bars.map((bar) => (
        <div key={bar.key} className="rounded-2xl border border-slate-200 bg-slate-50/80 px-4 py-3">
          <div className="mb-3 flex items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <span
                className="inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold"
                style={{ backgroundColor: `${bar.color}12`, color: bar.color }}
              >
                {bar.label}
              </span>
              <span className="text-xs text-slate-500">{Math.round(bar.coverage)}% coverage</span>
            </div>
            <span className="text-lg font-bold tabular-nums" style={{ color: bar.color }}>
              {bar.value}
            </span>
          </div>
          <div className="h-2.5 overflow-hidden rounded-full bg-slate-200">
            <div
              className="h-full rounded-full transition-all duration-500 ease-out"
              style={{
                width: `${(bar.value / total) * 100}%`,
                backgroundColor: bar.color,
              }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
