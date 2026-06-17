"use client";

import type { GapAnalysis } from "@/types";

interface GapAnalysisTableProps {
  gaps: GapAnalysis[];
  isLoading?: boolean;
  onCreatePR?: (gapId: number) => void;
}

const RISK_CONFIG = {
  high: { color: "red", bg: "bg-red-50 dark:bg-red-900/20", badge: "bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200" },
  medium: { color: "amber", bg: "bg-amber-50 dark:bg-amber-900/20", badge: "bg-amber-100 dark:bg-amber-900 text-amber-800 dark:text-amber-200" },
  low: { color: "green", bg: "bg-green-50 dark:bg-green-900/20", badge: "bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200" },
};

const STATUS_CONFIG = {
  open: { icon: "🔴", label: "Open", color: "text-red-600 dark:text-red-400" },
  in_progress: { icon: "🟡", label: "In Progress", color: "text-amber-600 dark:text-amber-400" },
  resolved: { icon: "🟢", label: "Resolved", color: "text-green-600 dark:text-green-400" },
  mitigated: { icon: "🔵", label: "Mitigated", color: "text-blue-600 dark:text-blue-400" },
};

export function GapAnalysisTable({ gaps, isLoading = false, onCreatePR }: GapAnalysisTableProps) {
  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-48">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-3"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading gap analysis...</p>
        </div>
      </div>
    );
  }

  if (!gaps || gaps.length === 0) {
    return (
      <div className="text-center py-12 border border-dashed border-gray-300 dark:border-gray-700 rounded-lg">
        <span className="text-4xl mb-3 block">✨</span>
        <p className="text-gray-600 dark:text-gray-400 font-medium">No gaps found</p>
        <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">All obligations are fully covered</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700">
      <table className="w-full text-sm">
        <thead className="bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
          <tr>
            <th className="px-4 py-3 text-left font-semibold text-gray-900 dark:text-white">Status</th>
            <th className="px-4 py-3 text-left font-semibold text-gray-900 dark:text-white">Gap Summary</th>
            <th className="px-4 py-3 text-left font-semibold text-gray-900 dark:text-white">Coverage Score</th>
            <th className="px-4 py-3 text-left font-semibold text-gray-900 dark:text-white">Risk Level</th>
            <th className="px-4 py-3 text-left font-semibold text-gray-900 dark:text-white">Recommendation</th>
            <th className="px-4 py-3 text-left font-semibold text-gray-900 dark:text-white">Action</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
          {gaps.map((gap) => {
            const riskLevel = (gap.risk_level?.toLowerCase() || "medium") as keyof typeof RISK_CONFIG;
            const status = (gap.status?.toLowerCase() || "open") as keyof typeof STATUS_CONFIG;
            const riskConfig = RISK_CONFIG[riskLevel] || RISK_CONFIG.medium;
            const statusConfig = STATUS_CONFIG[status] || STATUS_CONFIG.open;

            return (
              <tr key={gap.id} className="hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors">
                <td className="px-4 py-3">
                  <span className={`inline-flex items-center gap-1 ${statusConfig.color}`}>
                    {statusConfig.icon}
                    <span className="text-xs font-medium">{statusConfig.label}</span>
                  </span>
                </td>
                <td className="px-4 py-3">
                  <p className="text-gray-900 dark:text-white font-medium line-clamp-2">{gap.gap_summary}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Obligation {gap.obligation_id}
                  </p>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className="w-16 bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-blue-600 h-2 rounded-full transition-all"
                        style={{ width: `${gap.coverage_score || 0}%` }}
                      ></div>
                    </div>
                    <span className="text-sm font-semibold text-gray-900 dark:text-white w-8">
                      {Math.round(gap.coverage_score || 0)}%
                    </span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className={`inline-block px-2 py-1 rounded text-xs font-semibold ${riskConfig.badge}`}>
                    {riskLevel.toUpperCase()}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <p className="text-gray-700 dark:text-gray-300 line-clamp-2 text-xs">{gap.recommended_action}</p>
                </td>
                <td className="px-4 py-3">
                  <button
                    onClick={() => onCreatePR?.(gap.id)}
                    className="inline-flex items-center gap-1 px-3 py-1 bg-blue-600 hover:bg-blue-700 text-white rounded text-xs font-medium transition-colors"
                  >
                    📝 Create PR
                  </button>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
