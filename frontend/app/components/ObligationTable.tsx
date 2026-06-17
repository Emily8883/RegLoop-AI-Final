"use client";

import type { Obligation } from "@/types";

interface ObligationTableProps {
  obligations: Obligation[];
  isLoading?: boolean;
}

const priorityConfig: Record<string, { icon: string; color: string; bg: string }> = {
  high: { icon: "🔴", color: "text-red-900 dark:text-red-200", bg: "bg-red-100 dark:bg-red-900/30" },
  medium: {
    icon: "🟡",
    color: "text-amber-900 dark:text-amber-200",
    bg: "bg-amber-100 dark:bg-amber-900/30",
  },
  low: { icon: "🟢", color: "text-green-900 dark:text-green-200", bg: "bg-green-100 dark:bg-green-900/30" },
};

export function ObligationTable({ obligations, isLoading = false }: ObligationTableProps) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="flex items-center gap-4 p-4 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse"
          >
            <div className="w-10 h-10 bg-slate-200 dark:bg-slate-700 rounded" />
            <div className="flex-1 space-y-2">
              <div className="h-4 w-40 bg-slate-200 dark:bg-slate-700 rounded" />
              <div className="h-3 w-56 bg-slate-200 dark:bg-slate-700 rounded" />
            </div>
            <div className="h-6 w-16 bg-slate-200 dark:bg-slate-700 rounded" />
          </div>
        ))}
      </div>
    );
  }

  if (obligations.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-center">
        <span className="text-4xl mb-3">✓</span>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          No obligations found. Upload a document to extract obligations.
        </p>
      </div>
    );
  }

  const recentObligations = obligations.slice(0, 5);

  return (
    <div className="space-y-2" role="region" aria-label="Recent obligations list">
      {recentObligations.map((obligation, index) => {
        const priority = obligation.priority || "medium";
        const priorityStyle = priorityConfig[priority] || priorityConfig.medium;

        return (
          <div
            key={obligation.id}
            className="animate-slideInUp rounded-lg border border-slate-200/50 dark:border-slate-700/50 bg-slate-50/50 dark:bg-slate-800/30 p-4 hover:bg-slate-100/50 dark:hover:bg-slate-800/50 transition-all duration-200"
            style={{ animationDelay: `${index * 50}ms` }}
            role="article"
            aria-label={`Obligation: ${obligation.obligation_id} - ${priority} priority`}
          >
            {/* Row Layout */}
            <div className="flex items-start gap-4">
              {/* Priority Icon */}
              <div className="flex-shrink-0 text-xl" aria-hidden="true">
                {priorityStyle.icon}
              </div>

              {/* Main Content */}
              <div className="flex-1 min-w-0">
                <div className="flex items-baseline gap-3 mb-2">
                  <p className="font-semibold text-slate-900 dark:text-white line-clamp-1">
                    {obligation.obligation_id}
                  </p>
                  <span
                    className="text-xs px-2 py-1 rounded bg-slate-200/50 dark:bg-slate-700/50 text-slate-700 dark:text-slate-300 font-medium flex-shrink-0"
                    aria-label={`Category: ${obligation.category}`}
                  >
                    {obligation.category}
                  </span>
                </div>
                <p className="text-sm text-slate-700 dark:text-slate-300 line-clamp-2 mb-2">
                  {obligation.obligation_text}
                </p>
                <p className="text-xs text-slate-600 dark:text-slate-400">
                  👥 {obligation.responsible_team}
                </p>
              </div>

              {/* Priority Badge */}
              <div
                className={`flex-shrink-0 inline-flex items-center gap-1 rounded-full ${priorityStyle.bg} px-3 py-1`}
                aria-label={`Priority: ${priority}`}
              >
                <span className={`text-xs font-semibold ${priorityStyle.color} capitalize`}>
                  {priority}
                </span>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}
