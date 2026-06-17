"use client";

import type { ReactNode } from "react";
import { BarChart3, CheckCircle2, Cog, FileText, FolderOpen } from "lucide-react";
import type { ComplianceSummary } from "@/types";

interface MetricCardProps {
  title: string;
  value: string | number;
  helper: string;
  icon: ReactNode;
  accent: "blue" | "green" | "violet" | "amber";
  isLoading?: boolean;
}

function MetricCard({
  title,
  value,
  helper,
  icon,
  accent,
  isLoading = false,
}: MetricCardProps) {
  const accents = {
    blue: "bg-blue-50 text-blue-600 ring-blue-100",
    green: "bg-emerald-50 text-emerald-600 ring-emerald-100",
    violet: "bg-violet-50 text-violet-600 ring-violet-100",
    amber: "bg-amber-50 text-amber-600 ring-amber-100",
  };

  return (
    <div className="rounded-[26px] border border-slate-200 bg-white p-5 shadow-sm transition-all duration-200 hover:-translate-y-0.5 hover:shadow-md">
      <div className="flex items-start justify-between gap-4">
        <div className="space-y-3">
          <p className="text-sm font-semibold text-slate-500">{title}</p>
          {isLoading ? (
            <div className="h-10 w-24 animate-pulse rounded-xl bg-slate-200" />
          ) : (
            <p className="text-[2rem] font-bold leading-none tracking-tight text-slate-950">{value}</p>
          )}
        </div>
        <span
          className={`flex h-12 w-12 items-center justify-center rounded-2xl ring-1 ${accents[accent]}`}
        >
          {icon}
        </span>
      </div>
      <div className="mt-5 flex items-center gap-2 text-xs font-medium text-slate-500">
        <span className="h-2 w-2 rounded-full bg-current opacity-70" />
        <span>{helper}</span>
      </div>
    </div>
  );
}

interface DashboardCardsProps {
  totalDocuments: number;
  totalObligations: number;
  complianceData: ComplianceSummary | null;
  isLoading: boolean;
}

export function DashboardCards({
  totalDocuments,
  totalObligations,
  complianceData,
  isLoading,
}: DashboardCardsProps) {
  const categoryCounts: Record<string, number> = {};
  if (complianceData?.categories) {
    complianceData.categories.forEach((category) => {
      categoryCounts[category.category.toLowerCase()] = category.total_obligations ?? 0;
    });
  }

  const complianceScore = complianceData?.overall_compliance_score ?? 0;

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-5">
      <MetricCard
        title="Total Documents"
        value={totalDocuments}
        helper="+2 uploaded this week"
        icon={<FileText className="h-5 w-5" />}
        accent="blue"
        isLoading={isLoading}
      />
      <MetricCard
        title="Total Obligations"
        value={totalObligations}
        helper="Active obligations"
        icon={<CheckCircle2 className="h-5 w-5" />}
        accent="green"
        isLoading={isLoading}
      />
      <MetricCard
        title="Compliance Score"
        value={`${complianceScore.toFixed(1)}%`}
        helper="Overall score"
        icon={<BarChart3 className="h-5 w-5" />}
        accent="violet"
        isLoading={isLoading}
      />
      <MetricCard
        title="Reporting"
        value={categoryCounts.reporting ?? 0}
        helper="Pending actions"
        icon={<FolderOpen className="h-5 w-5" />}
        accent="amber"
        isLoading={isLoading}
      />
      <MetricCard
        title="Operational"
        value={categoryCounts.operational ?? 0}
        helper="Active items"
        icon={<Cog className="h-5 w-5" />}
        accent="blue"
        isLoading={isLoading}
      />
    </div>
  );
}
