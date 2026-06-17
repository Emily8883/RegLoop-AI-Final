"use client";

import { useState } from "react";
import type { PolicyPullRequest } from "@/types";

interface PolicyReviewCardProps {
  pr: PolicyPullRequest;
  onApprove?: (prId: number) => void;
  onReject?: (prId: number) => void;
  onModify?: (prId: number) => void;
  onEscalate?: (prId: number) => void;
  isLoading?: boolean;
}

const STATUS_CONFIG = {
  pending: {
    icon: "Pending",
    label: "Pending Review",
    color: "bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800",
  },
  approved: {
    icon: "Approved",
    label: "Approved",
    color: "bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800",
  },
  rejected: {
    icon: "Rejected",
    label: "Rejected",
    color: "bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800",
  },
  escalated: {
    icon: "Escalated",
    label: "Escalated",
    color: "bg-orange-50 dark:bg-orange-900/20 border-orange-200 dark:border-orange-800",
  },
  modified: {
    icon: "Modified",
    label: "Modified",
    color: "bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800",
  },
};

export function PolicyReviewCard({
  pr,
  onApprove,
  onReject,
  onModify,
  onEscalate,
  isLoading = false,
}: PolicyReviewCardProps) {
  const [showDetails, setShowDetails] = useState(false);
  const [selectedAction, setSelectedAction] = useState<string | null>(null);

  const status = (pr.status?.toLowerCase() || "pending") as keyof typeof STATUS_CONFIG;
  const statusConfig = STATUS_CONFIG[status] || STATUS_CONFIG.pending;
  const riskLevel = (pr.risk_level?.toLowerCase() || "medium") as "high" | "medium" | "low";

  const getRiskColor = (risk: string) => {
    switch (risk.toLowerCase()) {
      case "high":
        return "bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200";
      case "low":
        return "bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200";
      default:
        return "bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200";
    }
  };

  return (
    <div className={`rounded-lg border-2 p-6 transition-all ${statusConfig.color}`}>
      <div className="mb-4 flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="mb-2 flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wide text-gray-600 dark:text-gray-300">
              {statusConfig.icon}
            </span>
            <span className="text-xs font-semibold text-gray-500 dark:text-gray-400">
              {statusConfig.label}
            </span>
          </div>
          <h3 className="mb-2 text-lg font-bold text-gray-900 dark:text-white">Amendment #{pr.id}</h3>
          <p className="line-clamp-2 text-sm text-gray-700 dark:text-gray-300">{pr.gap_description}</p>
        </div>
        <div className="flex flex-col items-end gap-2">
          <span className={`rounded-full px-3 py-1 text-xs font-semibold ${getRiskColor(riskLevel)}`}>
            {riskLevel.toUpperCase()} RISK
          </span>
          {pr.confidence_score !== undefined && (
            <span className="text-xs text-gray-600 dark:text-gray-400">
              Confidence: {Math.round(pr.confidence_score * 100)}%
            </span>
          )}
        </div>
      </div>

      <div className="mb-4 grid grid-cols-1 gap-3 border-b border-gray-300 pb-4 sm:grid-cols-2 dark:border-gray-700">
        <div>
          <label className="text-xs font-semibold uppercase text-gray-600 dark:text-gray-400">
            Regulatory Citation
          </label>
          <p className="font-mono text-sm text-gray-900 dark:text-white">{pr.regulatory_citation || "N/A"}</p>
        </div>
        <div>
          <label className="text-xs font-semibold uppercase text-gray-600 dark:text-gray-400">
            Suggested Owner
          </label>
          <p className="text-sm text-gray-900 dark:text-white">{pr.suggested_owner || "To be assigned"}</p>
        </div>
      </div>

      <div className="mb-4 rounded border border-blue-200 bg-blue-50 p-3 dark:border-blue-800 dark:bg-blue-900/20">
        <label className="mb-2 block text-xs font-semibold uppercase text-gray-700 dark:text-gray-300">
          Proposed Amendment
        </label>
        <p className="line-clamp-3 font-mono text-sm text-gray-900 dark:text-white">
          {pr.proposed_amendment || "No amendment details available"}
        </p>
      </div>

      <button
        onClick={() => setShowDetails(!showDetails)}
        className="mb-4 text-sm font-medium text-blue-600 hover:underline dark:text-blue-400"
      >
        {showDetails ? "Hide Details" : "View Full Details"}
      </button>

      {showDetails && (
        <div className="mb-4 space-y-3 rounded border border-gray-200 bg-white p-4 dark:border-gray-700 dark:bg-gray-800">
          <div>
            <label className="block text-xs font-semibold uppercase text-gray-600 dark:text-gray-400">
              Before (Current Policy)
            </label>
            <pre className="overflow-x-auto rounded bg-gray-100 p-2 text-xs text-gray-800 dark:bg-gray-900 dark:text-gray-200">
              {pr.before_text || pr.original_policy_text || "No original policy text"}
            </pre>
          </div>
          <div>
            <label className="block text-xs font-semibold uppercase text-gray-600 dark:text-gray-400">
              After (Proposed Change)
            </label>
            <pre className="overflow-x-auto rounded bg-gray-100 p-2 text-xs text-gray-800 dark:bg-gray-900 dark:text-gray-200">
              {pr.after_text || pr.proposed_amendment || "No amendment details"}
            </pre>
          </div>
          {pr.diff_summary && (
            <div>
              <label className="block text-xs font-semibold uppercase text-gray-600 dark:text-gray-400">
                Diff Summary
              </label>
              <p className="text-sm text-gray-700 dark:text-gray-300">{pr.diff_summary}</p>
            </div>
          )}
        </div>
      )}

      {status === "pending" ? (
        <div className="grid gap-2 md:grid-cols-4">
          <button
            onClick={() => {
              setSelectedAction("approve");
              onApprove?.(pr.id);
            }}
            disabled={isLoading || selectedAction === "approve"}
            className="rounded bg-green-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-green-700 disabled:bg-gray-400"
          >
            {selectedAction === "approve" && isLoading ? "Approving..." : "Approve"}
          </button>
          <button
            onClick={() => {
              setSelectedAction("reject");
              onReject?.(pr.id);
            }}
            disabled={isLoading || selectedAction === "reject"}
            className="rounded bg-red-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-red-700 disabled:bg-gray-400"
          >
            {selectedAction === "reject" && isLoading ? "Rejecting..." : "Reject"}
          </button>
          <button
            onClick={() => {
              setSelectedAction("modify");
              onModify?.(pr.id);
            }}
            disabled={isLoading || selectedAction === "modify"}
            className="rounded bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700 disabled:bg-gray-400"
          >
            {selectedAction === "modify" && isLoading ? "Updating..." : "Modify"}
          </button>
          <button
            onClick={() => {
              setSelectedAction("escalate");
              onEscalate?.(pr.id);
            }}
            disabled={isLoading || selectedAction === "escalate"}
            className="rounded bg-orange-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-orange-700 disabled:bg-gray-400"
          >
            {selectedAction === "escalate" && isLoading ? "Escalating..." : "Escalate"}
          </button>
        </div>
      ) : (
        <div className="text-xs italic text-gray-600 dark:text-gray-400">
          This recommendation is {statusConfig.label.toLowerCase()} and cannot be modified.
        </div>
      )}
    </div>
  );
}
