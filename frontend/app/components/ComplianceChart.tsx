"use client";

import type { ComplianceSummary } from "@/types";

interface ComplianceChartProps {
  data: ComplianceSummary | null;
  isLoading?: boolean;
}

export function ComplianceChart({ data, isLoading = false }: ComplianceChartProps) {
  const categories = data?.categories || [];
  const maxObligation = Math.max(...categories.map((c) => c.total_obligations), 1);

  const categoryColors = [
    { name: "color-1", bg: "bg-blue-500", accent: "bg-blue-100 dark:bg-blue-900/30" },
    { name: "color-2", bg: "bg-green-500", accent: "bg-green-100 dark:bg-green-900/30" },
    { name: "color-3", bg: "bg-purple-500", accent: "bg-purple-100 dark:bg-purple-900/30" },
    { name: "color-4", bg: "bg-amber-500", accent: "bg-amber-100 dark:bg-amber-900/30" },
    { name: "color-5", bg: "bg-rose-500", accent: "bg-rose-100 dark:bg-rose-900/30" },
    { name: "color-6", bg: "bg-cyan-500", accent: "bg-cyan-100 dark:bg-cyan-900/30" },
  ];

  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="space-y-2">
            <div className="flex items-center justify-between">
              <div className="h-4 w-24 bg-slate-200 dark:bg-slate-700 rounded animate-pulse" />
              <div className="h-4 w-12 bg-slate-200 dark:bg-slate-700 rounded animate-pulse" />
            </div>
            <div className="h-8 bg-slate-200 dark:bg-slate-700 rounded animate-pulse" />
          </div>
        ))}
      </div>
    );
  }

  if (categories.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <span className="text-4xl mb-3">📊</span>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          No category data available yet. Upload documents to analyze.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {categories.map((category, index) => {
        const percentage = (category.total_obligations / maxObligation) * 100;
        const color = categoryColors[index % categoryColors.length];

        return (
          <div
            key={category.category}
            className={`animate-slideInUp rounded-lg p-6 ${color.accent} border-2 border-slate-200/70 dark:border-slate-700/70 transition-all duration-300 hover:shadow-lg hover:border-blue-400 dark:hover:border-blue-500`}
            style={{ animationDelay: `${index * 50}ms` }}
          >
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className={`w-4 h-4 rounded-full ${color.bg}`} />
                <h4 className="font-bold text-slate-900 dark:text-white text-base">
                  {category.category}
                </h4>
              </div>
              <div className="text-right">
                <p className="text-xl font-bold text-slate-900 dark:text-white">
                  {category.total_obligations}
                </p>
                <p className="text-xs text-slate-600 dark:text-slate-400 mt-1">
                  {Math.round(category.average_coverage)}% covered
                </p>
              </div>
            </div>

            {/* Bar Chart */}
            <div className="space-y-3">
              {/* Obligation Bar */}
              <div>
                <div className="text-xs font-bold text-slate-600 dark:text-slate-400 mb-2">
                  Obligation Count
                </div>
                <div className="w-full h-7 bg-slate-300 dark:bg-slate-700 rounded-lg overflow-hidden border border-slate-200 dark:border-slate-600">
                  <div
                    className={`h-full ${color.bg} transition-all duration-500 flex items-center justify-end pr-3 shadow-md`}
                    style={{ width: `${percentage}%` }}
                  >
                    {percentage > 20 && (
                      <span className="text-xs font-bold text-white">
                        {category.total_obligations}
                      </span>
                    )}
                  </div>
                </div>
              </div>

              {/* Coverage Bar */}
              <div>
                <div className="text-xs text-slate-600 dark:text-slate-400 mb-1.5">
                  Coverage
                </div>
                <div className="w-full h-6 bg-slate-200 dark:bg-slate-700 rounded-md overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-green-500 to-emerald-500 transition-all duration-500 flex items-center justify-end pr-2"
                    style={{ width: `${category.average_coverage}%` }}
                  >
                    {category.average_coverage > 20 && (
                      <span className="text-xs font-bold text-white">
                        {Math.round(category.average_coverage)}%
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
