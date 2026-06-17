"use client";

import type { ComplianceSummary } from "@/types";

interface DashboardCardsProps {
  totalDocuments: number;
  totalObligations: number;
  complianceData: ComplianceSummary | null;
  isLoading?: boolean;
}

export function DashboardCards({
  totalDocuments,
  totalObligations,
  complianceData,
  isLoading = false,
}: DashboardCardsProps) {
  const complianceScore = complianceData?.overall_compliance_score || 0;
  const skeletonClass = isLoading ? "animate-pulse" : "";

  const cards = [
    {
      icon: "📄",
      label: "Total Documents",
      value: totalDocuments,
      color: "blue",
      delay: "0ms",
    },
    {
      icon: "✓",
      label: "Total Obligations",
      value: totalObligations,
      color: "green",
      delay: "100ms",
    },
    {
      icon: "📊",
      label: "Compliance Score",
      value: `${Math.round(complianceScore)}%`,
      color: "purple",
      delay: "200ms",
    },
  ];

  const colorClasses: Record<string, { bg: string; text: string; accent: string }> = {
    blue: {
      bg: "bg-blue-50 dark:bg-blue-900/20",
      text: "text-blue-900 dark:text-blue-100",
      accent: "text-blue-600 dark:text-blue-400",
    },
    green: {
      bg: "bg-green-50 dark:bg-green-900/20",
      text: "text-green-900 dark:text-green-100",
      accent: "text-green-600 dark:text-green-400",
    },
    purple: {
      bg: "bg-purple-50 dark:bg-purple-900/20",
      text: "text-purple-900 dark:text-purple-100",
      accent: "text-purple-600 dark:text-purple-400",
    },
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
      {cards.map((card) => {
        const colors = colorClasses[card.color];
        return (
          <div
            key={card.label}
            className={`animate-scaleIn rounded-xl border-2 border-slate-200/80 dark:border-slate-700/80 ${colors.bg} p-8 shadow-lg hover:shadow-2xl hover:border-blue-400 dark:hover:border-blue-500 transition-all duration-300 hover:-translate-y-1`}
            style={{ animationDelay: card.delay }}
          >
            {/* Icon */}
            <div className="flex items-start justify-between mb-6">
              <span className="text-5xl">{card.icon}</span>
              <div className="w-16 h-16 rounded-lg bg-white dark:bg-slate-800 flex items-center justify-center shadow-lg border border-slate-200 dark:border-slate-700">
                <span className={`text-2xl font-bold ${colors.accent}`}>→</span>
              </div>
            </div>

            {/* Content */}
            <div className="space-y-3">
              <p className="text-sm font-bold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                {card.label}
              </p>
              <div className={`text-5xl font-bold ${colors.text} ${skeletonClass}`}>
                {card.value}
              </div>
            </div>

            {/* Progress Bar - For Compliance Score */}
            {card.label === "Compliance Score" && (
              <div className="mt-6 pt-6 border-t-2 border-slate-200/50 dark:border-slate-700/50">
                <div className="flex items-center justify-between mb-3">
                  <span className="text-xs font-bold text-slate-600 dark:text-slate-400">
                    OVERALL SCORE
                  </span>
                  <span className={`text-sm font-bold ${colors.accent}`}>
                    {Math.round(complianceScore)}%
                  </span>
                </div>
                <div className="w-full h-3 bg-slate-300 dark:bg-slate-700 rounded-full overflow-hidden border border-slate-200 dark:border-slate-600">
                  <div
                    className={`h-full bg-gradient-to-r from-purple-500 to-purple-600 transition-all duration-500 rounded-full shadow-md`}
                    style={{ width: `${complianceScore}%` }}
                  />
                </div>
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
}
