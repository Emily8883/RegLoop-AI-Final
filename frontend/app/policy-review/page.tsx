"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/services/api";
import { PolicyReviewCard } from "@/app/components/PolicyReviewCard";
import type { PolicyPullRequest } from "@/types";

const REVIEWER_NAME = "Compliance Analyst";

export default function PolicyReviewPage() {
  const [prs, setPRs] = useState<PolicyPullRequest[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [selectedStatus, setSelectedStatus] = useState<string>("pending");
  const [actionLoading, setActionLoading] = useState<number | null>(null);

  const fetchPRs = async () => {
    setIsLoading(true);
    setError(null);

    const response = await apiClient.getPolicyPRs();
    if (response.error) {
      setError(response.error);
      setPRs([]);
    } else {
      setPRs(response.data || []);
    }

    setIsLoading(false);
  };

  useEffect(() => {
    fetchPRs();
  }, []);

  const submitReviewAction = async (prId: number, action: "approve" | "reject" | "modify" | "escalate") => {
    setActionLoading(prId);
    setError(null);
    setNotice(null);

    const comments =
      action === "modify" || action === "escalate"
        ? window.prompt(`Add ${action} notes for PR #${prId}`, "")
        : "";

    const response = await apiClient.reviewPolicyPR(prId, {
      reviewerName: REVIEWER_NAME,
      action,
      comments: comments || "",
    });

    if (response.error) {
      setError(response.error);
    } else {
      setNotice(`PR #${prId} marked as ${response.data.new_status || action}.`);
      await fetchPRs();
    }

    setActionLoading(null);
  };

  const filteredPRs = selectedStatus
    ? prs.filter((pr) => pr.status?.toLowerCase() === selectedStatus.toLowerCase())
    : prs;

  const stats = {
    total: prs.length,
    pending: prs.filter((p) => p.status?.toLowerCase() === "pending").length,
    approved: prs.filter((p) => p.status?.toLowerCase() === "approved").length,
    rejected: prs.filter((p) => p.status?.toLowerCase() === "rejected").length,
    escalated: prs.filter((p) => p.status?.toLowerCase() === "escalated").length,
  };

  return (
    <div className="page-shell bg-gradient-to-br from-slate-50 via-white to-purple-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-800">
      <header className="sticky top-0 z-40 border-b border-slate-200/80 bg-white/95 shadow-sm backdrop-blur-xl dark:border-slate-700/80 dark:bg-slate-950/95">
        <div className="container-modern py-7">
          <Link
            href="/"
            className="mb-3 inline-flex items-center gap-2 text-sm font-medium text-slate-600 transition-colors hover:text-blue-600 dark:text-slate-400 dark:hover:text-blue-400"
          >
            <span>Back to Dashboard</span>
          </Link>
          <div className="space-y-2">
            <h1 className="text-4xl font-bold text-slate-900 dark:text-white">Policy Recommendations</h1>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Review and approve proposed policy amendments with human-in-the-loop control.
            </p>
          </div>
        </div>
      </header>

      <main className="container-modern space-y-8 py-8">
        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 shadow-sm dark:border-red-800 dark:bg-red-900/20">
            <p className="text-sm font-medium text-red-800 dark:text-red-200">{error}</p>
          </div>
        )}

        {notice && (
          <div className="rounded-lg border border-green-200 bg-green-50 p-4 shadow-sm dark:border-green-800 dark:bg-green-900/20">
            <p className="text-sm font-medium text-green-800 dark:text-green-200">{notice}</p>
          </div>
        )}

        <div className="grid grid-cols-1 gap-4 md:grid-cols-5">
          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
            <p className="text-xs font-semibold uppercase text-slate-600 dark:text-slate-400">Total PRs</p>
            <p className="mt-2 text-3xl font-bold text-slate-900 dark:text-white">{stats.total}</p>
          </div>
          <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-6 shadow-sm dark:border-yellow-800 dark:bg-yellow-900/20">
            <p className="text-xs font-semibold uppercase text-yellow-700 dark:text-yellow-300">Pending</p>
            <p className="mt-2 text-3xl font-bold text-yellow-600 dark:text-yellow-400">{stats.pending}</p>
          </div>
          <div className="rounded-lg border border-green-200 bg-green-50 p-6 shadow-sm dark:border-green-800 dark:bg-green-900/20">
            <p className="text-xs font-semibold uppercase text-green-700 dark:text-green-300">Approved</p>
            <p className="mt-2 text-3xl font-bold text-green-600 dark:text-green-400">{stats.approved}</p>
          </div>
          <div className="rounded-lg border border-red-200 bg-red-50 p-6 shadow-sm dark:border-red-800 dark:bg-red-900/20">
            <p className="text-xs font-semibold uppercase text-red-700 dark:text-red-300">Rejected</p>
            <p className="mt-2 text-3xl font-bold text-red-600 dark:text-red-400">{stats.rejected}</p>
          </div>
          <div className="rounded-lg border border-orange-200 bg-orange-50 p-6 shadow-sm dark:border-orange-800 dark:bg-orange-900/20">
            <p className="text-xs font-semibold uppercase text-orange-700 dark:text-orange-300">Escalated</p>
            <p className="mt-2 text-3xl font-bold text-orange-600 dark:text-orange-400">{stats.escalated}</p>
          </div>
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-900">
          <p className="mb-3 text-sm font-semibold text-slate-700 dark:text-slate-300">Filter by Status</p>
          <div className="flex flex-wrap gap-2">
            {[
              { key: "", label: `All (${stats.total})` },
              { key: "pending", label: `Pending (${stats.pending})` },
              { key: "approved", label: `Approved (${stats.approved})` },
              { key: "rejected", label: `Rejected (${stats.rejected})` },
              { key: "escalated", label: `Escalated (${stats.escalated})` },
            ].map((option) => (
              <button
                key={option.key || "all"}
                onClick={() => setSelectedStatus(option.key)}
                className={`rounded px-4 py-2 text-sm font-medium transition-colors ${
                  selectedStatus === option.key
                    ? "bg-blue-600 text-white"
                    : "bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        {isLoading ? (
          <div className="flex h-48 items-center justify-center">
            <div className="mx-auto h-8 w-8 animate-spin rounded-full border-b-2 border-blue-600" />
          </div>
        ) : filteredPRs.length === 0 ? (
          <div className="rounded-lg border border-dashed border-slate-300 py-12 text-center dark:border-slate-700">
            <p className="font-medium text-slate-600 dark:text-slate-400">No recommendations found</p>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-500">
              {selectedStatus ? `No ${selectedStatus} recommendations yet.` : "Run gap analysis to generate policy recommendations."}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredPRs.map((pr) => (
              <PolicyReviewCard
                key={pr.id}
                pr={pr}
                onApprove={(prId) => submitReviewAction(prId, "approve")}
                onReject={(prId) => submitReviewAction(prId, "reject")}
                onModify={(prId) => submitReviewAction(prId, "modify")}
                onEscalate={(prId) => submitReviewAction(prId, "escalate")}
                isLoading={actionLoading === pr.id}
              />
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
