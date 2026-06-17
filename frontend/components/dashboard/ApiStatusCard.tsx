"use client";

import { Link2, ShieldCheck } from "lucide-react";

interface ApiStatusCardProps {
  backendUrl: string;
}

export function ApiStatusCard({ backendUrl }: ApiStatusCardProps) {
  return (
    <div className="rounded-[26px] border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex items-center gap-3">
        <span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-emerald-50 text-emerald-600">
          <ShieldCheck className="h-5 w-5" />
        </span>
        <div>
          <p className="text-sm font-semibold text-slate-950">API Connection</p>
          <p className="text-xs text-slate-500">Backend is connected and running smoothly</p>
        </div>
      </div>
      <div className="mt-4 rounded-2xl bg-slate-50 p-4 ring-1 ring-slate-200">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">
            <Link2 className="h-3.5 w-3.5" />
            Backend
          </div>
          <span className="rounded-full bg-emerald-100 px-2.5 py-1 text-xs font-semibold text-emerald-700">
            Connected
          </span>
        </div>
        <p className="mt-2 break-all text-sm font-medium text-blue-600">{backendUrl}</p>
        <p className="mt-3 text-xs text-slate-500">Last checked: Just now</p>
      </div>
    </div>
  );
}
