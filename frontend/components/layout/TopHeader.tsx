"use client";

import { Bell, CalendarDays, Search } from "lucide-react";
import { ExportButton } from "@/app/components/ExportDropdown";

interface TopHeaderProps {
  title: string;
  subtitle: string;
}

export function TopHeader({ title, subtitle }: TopHeaderProps) {
  return (
    <header className="rounded-[28px] border border-slate-200/80 bg-white/90 px-5 py-4 shadow-[0_14px_40px_rgba(15,23,42,0.06)] backdrop-blur-xl sm:px-6">
      <div className="flex flex-col gap-4 xl:flex-row xl:items-center xl:justify-between">
        <div className="space-y-1">
          <p className="text-3xl font-bold tracking-tight text-slate-950">{title}</p>
          <p className="max-w-3xl text-sm text-slate-600 sm:text-base">{subtitle}</p>
        </div>

        <div className="flex flex-wrap items-center gap-3">
          <label className="hidden min-w-[220px] items-center gap-2 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-500 xl:flex">
            <Search className="h-4 w-4" />
            <input
              aria-label="Search dashboard"
              placeholder="Search dashboard"
              className="w-full bg-transparent text-sm text-slate-700 outline-none placeholder:text-slate-400"
            />
          </label>
          <button
            type="button"
            aria-label="Notifications"
            className="relative flex h-11 w-11 items-center justify-center rounded-2xl border border-slate-200 bg-slate-50 text-slate-500 shadow-sm"
          >
            <Bell className="h-4 w-4" />
            <span className="absolute right-2 top-2 h-2.5 w-2.5 rounded-full bg-red-500" />
          </button>
          <div className="hidden items-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-3 py-2.5 text-sm font-medium text-slate-700 sm:flex">
            <span className="flex h-9 w-9 items-center justify-center rounded-full bg-gradient-to-br from-violet-500 to-blue-500 text-xs font-bold text-white">
              RS
            </span>
            <span>RegLoop System</span>
          </div>
          <ExportButton />
        </div>
      </div>

      <div className="mt-4 flex flex-wrap items-center justify-between gap-3 border-t border-slate-200/80 pt-4">
        <div className="inline-flex items-center gap-2 rounded-full bg-emerald-50 px-3 py-1.5 text-sm font-semibold text-emerald-700">
          <span className="h-2 w-2 rounded-full bg-emerald-500" />
          Live Status: Connected
        </div>
        <button
          type="button"
          className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-medium text-slate-700 shadow-sm"
        >
          <CalendarDays className="h-4 w-4" />
          Today
        </button>
      </div>
    </header>
  );
}

