"use client";

import type { PriorityBreakdown } from "@/types";

interface PriorityChartProps {
  data: PriorityBreakdown | null;
  isLoading?: boolean;
}

export function PriorityChart({ data, isLoading = false }: PriorityChartProps) {
  const priorityBreakdown = data || {
    high: 0,
    medium: 0,
    low: 0,
    high_coverage: 0,
    medium_coverage: 0,
    low_coverage: 0,
  };

  const total =
    priorityBreakdown.high + priorityBreakdown.medium + priorityBreakdown.low || 1;

  const priorities = [
    {
      name: "High",
      icon: "🔴",
      count: priorityBreakdown.high,
      coverage: priorityBreakdown.high_coverage,
      color: "red",
      bg: "bg-red-50 dark:bg-red-900/20",
      bar: "bg-red-500",
    },
    {
      name: "Medium",
      icon: "🟡",
      count: priorityBreakdown.medium,
      coverage: priorityBreakdown.medium_coverage,
      color: "amber",
      bg: "bg-amber-50 dark:bg-amber-900/20",
      bar: "bg-amber-500",
    },
    {
      name: "Low",
      icon: "🟢",
      count: priorityBreakdown.low,
      coverage: priorityBreakdown.low_coverage,
      color: "green",
      bg: "bg-green-50 dark:bg-green-900/20",
      bar: "bg-green-500",
    },
  ];

  if (isLoading) {
    return (
      <div className="space-y-5">
        {[1, 2, 3].map((i) => (
          <div key={i} className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="h-5 w-24 bg-slate-200 dark:bg-slate-700 rounded animate-pulse" />
              <div className="h-5 w-20 bg-slate-200 dark:bg-slate-700 rounded animate-pulse" />
            </div>
            <div className="h-8 bg-slate-200 dark:bg-slate-700 rounded animate-pulse" />
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {priorities.map((priority, index) => {
        const percentage = (priority.count / total) * 100;

        return (
          <div
            key={priority.name}
            className={`animate-slideInUp rounded-lg p-6 ${priority.bg} border-2 border-slate-200/70 dark:border-slate-700/70 transition-all duration-300 hover:shadow-lg hover:border-blue-400 dark:hover:border-blue-500`}
            style={{ animationDelay: `${index * 50}ms` }}
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{priority.icon}</span>
                <span className="font-bold text-slate-900 dark:text-white text-lg">
                  {priority.name}
                </span>
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-slate-900 dark:text-white">
                  {priority.count}
                </p>
                <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                  {Math.round(percentage)}%
                </p>
              </div>
            </div>

            {/* Count Bar */}
            <div className="space-y-3">
              <div className="w-full h-5 bg-slate-300 dark:bg-slate-700 rounded-full overflow-hidden border border-slate-200 dark:border-slate-600">
                <div
                  className={`h-full ${priority.bar} transition-all duration-500 shadow-md`}
                  style={{ width: `${percentage}%` }}
                />
              </div>

              {/* Coverage Info */}
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-600 dark:text-slate-400">
                  Coverage
                </span>
                <span className="text-xs font-bold text-slate-900 dark:text-white">
                  {Math.round(priority.coverage)}%
                </span>
              </div>
              <div className="w-full h-4 bg-slate-300 dark:bg-slate-700 rounded-full overflow-hidden border border-slate-200 dark:border-slate-600">
                <div
                  className="h-full bg-gradient-to-r from-blue-500 to-cyan-500 transition-all duration-500 shadow-md"
                  style={{ width: `${priority.coverage}%` }}
                />
              </div>
            </div>
          </div>
        );
      })}

      {/* Summary Stats */}
      <div className="mt-6 pt-6 border-t border-slate-200/50 dark:border-slate-700/50 grid grid-cols-3 gap-4">
        {priorities.map((priority) => (
          <div
            key={`summary-${priority.name}`}
            className="text-center p-3 rounded-lg bg-slate-100/50 dark:bg-slate-800/50"
          >
            <p className="text-xs text-slate-600 dark:text-slate-400 mb-1">
              {priority.name}
            </p>
            <p className="text-xl font-bold text-slate-900 dark:text-white">
              {priority.count}
            </p>
            <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
              {Math.round(priority.coverage)}% 🔒
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
