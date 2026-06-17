"use client";

import Link from "next/link";
import { FilePlus2, FileText, Sparkles } from "lucide-react";
import { ExportButton } from "@/app/components/ExportDropdown";

export function QuickActionsCard() {
  return (
    <div className="rounded-[26px] border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center gap-3">
        <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-violet-50 text-violet-600">
          <Sparkles className="h-5 w-5" />
        </span>
        <div>
          <p className="text-sm font-semibold text-slate-950">Quick Actions</p>
          <p className="text-xs text-slate-500">Jump into common compliance workflows</p>
        </div>
      </div>
      <div className="mt-4 space-y-3">
        <Link
          href="/documents"
          className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-semibold text-slate-700 transition-colors hover:bg-white hover:text-blue-600"
        >
          <FilePlus2 className="h-4 w-4" />
          Upload Document
        </Link>
        <Link
          href="/obligations"
          className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm font-semibold text-slate-700 transition-colors hover:bg-white hover:text-blue-600"
        >
          <FileText className="h-4 w-4" />
          Review Obligations
        </Link>
        <div className="rounded-2xl border border-slate-200 bg-slate-50 px-3 py-3">
          <ExportButton variant="small" />
        </div>
      </div>
    </div>
  );
}
