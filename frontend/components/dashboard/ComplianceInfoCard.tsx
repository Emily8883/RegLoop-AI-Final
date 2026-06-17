"use client";

import { ClipboardCheck } from "lucide-react";

interface ComplianceInfoCardProps {
  obligationsCount: number;
  complianceScore: number;
}

export function ComplianceInfoCard({
  obligationsCount,
  complianceScore,
}: ComplianceInfoCardProps) {
  return (
    <div className="overflow-hidden rounded-[26px] border border-slate-200 bg-white shadow-sm">
      <div className="bg-[radial-gradient(circle_at_top_left,rgba(37,99,235,0.10),transparent_55%),linear-gradient(180deg,#ffffff_0%,#f8fbff_100%)] p-5">
        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-blue-50 text-blue-600">
          <ClipboardCheck className="h-6 w-6" />
        </div>
        <p className="mt-5 text-lg font-semibold text-slate-950">Stay on top of your compliance obligations</p>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          Track active items, monitor category coverage, and keep your team aligned on regulatory follow-through.
        </p>
      </div>
      <div className="grid grid-cols-2 gap-3 border-t border-slate-200 bg-slate-50/70 px-5 py-4">
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Active obligations</p>
          <p className="mt-1 text-2xl font-bold text-slate-950">{obligationsCount}</p>
        </div>
        <div>
          <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Score</p>
          <p className="mt-1 text-2xl font-bold text-slate-950">{complianceScore.toFixed(1)}%</p>
        </div>
      </div>
    </div>
  );
}
