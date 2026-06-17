"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/services/api";
import { GapAnalysisTable } from "@/app/components/GapAnalysisTable";
import type { GapAnalysis, ComplianceSummary } from "@/types";

export default function CompliancePage() {
  const [gaps, setGaps] = useState<GapAnalysis[]>([]);
  const [summary, setSummary] = useState<ComplianceSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [selectedStatus, setSelectedStatus] = useState<string>("");
  const [creatingPrFor, setCreatingPrFor] = useState<number | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const [gapsRes, summaryRes] = await Promise.all([
          apiClient.getGapAnalysis(),
          apiClient.getComplianceSummary(),
        ]);

        if (gapsRes.error) {
          setError(gapsRes.error);
        } else {
          setGaps(gapsRes.data.gaps || []);
        }

        if (summaryRes.error) {
          console.error("Summary error:", summaryRes.error);
        } else {
          setSummary(summaryRes.data);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to load compliance data");
      } finally {
        setIsLoading(false);
      }
    };

    fetchData();
  }, []);

  const filteredGaps = selectedStatus
    ? gaps.filter((g) => g.status?.toLowerCase() === selectedStatus.toLowerCase())
    : gaps;

  const gapStats = {
    total: gaps.length,
    open: gaps.filter((g) => g.status?.toLowerCase() === "open").length,
    inProgress: gaps.filter((g) => g.status?.toLowerCase() === "in_progress").length,
    resolved: gaps.filter((g) => g.status?.toLowerCase() === "resolved").length,
  };

  const riskStats = {
    high: gaps.filter((g) => g.risk_level?.toLowerCase() === "high").length,
    medium: gaps.filter((g) => g.risk_level?.toLowerCase() === "medium").length,
    low: gaps.filter((g) => g.risk_level?.toLowerCase() === "low").length,
  };

  const avgCoverage =
    gaps.length > 0
      ? Math.round(gaps.reduce((sum, g) => sum + (g.coverage_score || 0), 0) / gaps.length)
      : 0;

  const handleCreatePR = async (gapId: number) => {
    setCreatingPrFor(gapId);
    setError(null);
    setNotice(null);

    const response = await apiClient.createPolicyPR(gapId);
    if (response.error) {
      setError(response.error);
    } else {
      setNotice(`Policy pull request #${response.data.pr_id} created for gap ${gapId}.`);
    }

    setCreatingPrFor(null);
  };

  return (
    <div className="page-shell bg-gradient-to-br from-slate-50 via-white to-blue-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-800">
      <header className="sticky top-0 z-40 border-b border-slate-200/80 bg-white/95 shadow-sm backdrop-blur-xl dark:border-slate-700/80 dark:bg-slate-950/95">
        <div className="container-modern py-7">
          <Link
            href="/"
            className="mb-3 inline-flex items-center gap-2 text-sm font-medium text-slate-600 transition-colors hover:text-blue-600 dark:text-slate-400 dark:hover:text-blue-400"
          >
            ← <span>Back to Dashboard</span>
          </Link>
          <div className="space-y-2">
            <h1 className="flex items-center gap-3 text-4xl font-bold text-slate-900 dark:text-white">
              <span className="text-4xl">📊</span>
              <span>Compliance Analysis</span>
            </h1>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              Review gaps, coverage scores, and compliance risks
            </p>
          </div>
        </div>
      </header>

      <main className="container-modern space-y-8 py-8">
        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 shadow-sm dark:border-red-800 dark:bg-red-900/20">
            <div className="flex items-start gap-3">
              <span className="text-xl">⚠️</span>
              <p className="text-sm font-medium text-red-800 dark:text-red-200">{error}</p>
            </div>
          </div>
        )}

        {notice && (
          <div className="rounded-lg border border-green-200 bg-green-50 p-4 shadow-sm dark:border-green-800 dark:bg-green-900/20">
            <p className="text-sm font-medium text-green-800 dark:text-green-200">{notice}</p>
          </div>
        )}

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md dark:border-slate-700 dark:bg-slate-900">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold uppercase text-slate-600 dark:text-slate-400">Total Gaps</p>
                <p className="mt-2 text-3xl font-bold text-slate-900 dark:text-white">{gapStats.total}</p>
              </div>
              <span className="text-4xl">📍</span>
            </div>
          </div>

          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm transition-shadow hover:shadow-md dark:border-slate-700 dark:bg-slate-900">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold uppercase text-slate-600 dark:text-slate-400">Avg Coverage</p>
                <p className="mt-2 text-3xl font-bold text-blue-600 dark:text-blue-400">{avgCoverage}%</p>
              </div>
              <span className="text-4xl">📈</span>
            </div>
          </div>

          <div className="rounded-lg border border-red-200 bg-red-50 p-6 shadow-sm transition-shadow hover:shadow-md dark:border-red-800 dark:bg-red-900/20">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold uppercase text-red-700 dark:text-red-300">High Risk</p>
                <p className="mt-2 text-3xl font-bold text-red-600 dark:text-red-400">{riskStats.high}</p>
              </div>
              <span className="text-4xl">⚠️</span>
            </div>
          </div>

          <div className="rounded-lg border border-orange-200 bg-orange-50 p-6 shadow-sm transition-shadow hover:shadow-md dark:border-orange-800 dark:bg-orange-900/20">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-xs font-semibold uppercase text-orange-700 dark:text-orange-300">Open Items</p>
                <p className="mt-2 text-3xl font-bold text-orange-600 dark:text-orange-400">{gapStats.open}</p>
              </div>
              <span className="text-4xl">🔴</span>
            </div>
          </div>
        </div>

        {summary && (
          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
            <h2 className="mb-6 text-lg font-bold text-slate-900 dark:text-white">Risk Distribution</h2>
            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
              <div>
                <h3 className="mb-4 text-sm font-semibold text-slate-700 dark:text-slate-300">By Risk Level</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-600 dark:text-slate-400">🔴 High</span>
                    <span className="font-bold text-slate-900 dark:text-white">{riskStats.high}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-600 dark:text-slate-400">🟡 Medium</span>
                    <span className="font-bold text-slate-900 dark:text-white">{riskStats.medium}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-600 dark:text-slate-400">🟢 Low</span>
                    <span className="font-bold text-slate-900 dark:text-white">{riskStats.low}</span>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="mb-4 text-sm font-semibold text-slate-700 dark:text-slate-300">By Status</h3>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-600 dark:text-slate-400">🔴 Open</span>
                    <span className="font-bold text-slate-900 dark:text-white">{gapStats.open}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-600 dark:text-slate-400">🟡 In Progress</span>
                    <span className="font-bold text-slate-900 dark:text-white">{gapStats.inProgress}</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-slate-600 dark:text-slate-400">🟢 Resolved</span>
                    <span className="font-bold text-slate-900 dark:text-white">{gapStats.resolved}</span>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="mb-4 text-sm font-semibold text-slate-700 dark:text-slate-300">Coverage Status</h3>
                <div className="relative h-32 overflow-hidden rounded-lg bg-slate-100 dark:bg-slate-800">
                  <div className="absolute inset-0 flex flex-col items-center justify-center">
                    <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">{avgCoverage}%</div>
                    <div className="mt-1 text-xs text-slate-600 dark:text-slate-400">Average Coverage</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="rounded-lg border border-slate-200 bg-white p-4 dark:border-slate-700 dark:bg-slate-900">
          <div className="flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedStatus("")}
              className={`rounded px-4 py-2 text-sm font-medium transition-colors ${
                selectedStatus === ""
                  ? "bg-blue-600 text-white"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
              }`}
            >
              All ({gapStats.total})
            </button>
            <button
              onClick={() => setSelectedStatus("open")}
              className={`rounded px-4 py-2 text-sm font-medium transition-colors ${
                selectedStatus === "open"
                  ? "bg-red-600 text-white"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
              }`}
            >
              Open ({gapStats.open})
            </button>
            <button
              onClick={() => setSelectedStatus("in_progress")}
              className={`rounded px-4 py-2 text-sm font-medium transition-colors ${
                selectedStatus === "in_progress"
                  ? "bg-yellow-600 text-white"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
              }`}
            >
              In Progress ({gapStats.inProgress})
            </button>
            <button
              onClick={() => setSelectedStatus("resolved")}
              className={`rounded px-4 py-2 text-sm font-medium transition-colors ${
                selectedStatus === "resolved"
                  ? "bg-green-600 text-white"
                  : "bg-slate-100 text-slate-700 hover:bg-slate-200 dark:bg-slate-800 dark:text-slate-300 dark:hover:bg-slate-700"
              }`}
            >
              Resolved ({gapStats.resolved})
            </button>
          </div>
        </div>

        <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
          <h2 className="mb-6 text-lg font-bold text-slate-900 dark:text-white">Gap Details</h2>
          <GapAnalysisTable
            gaps={filteredGaps}
            isLoading={isLoading || creatingPrFor !== null}
            onCreatePR={handleCreatePR}
          />
        </div>
      </main>
    </div>
  );
}
