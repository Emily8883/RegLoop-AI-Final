"use client";

import Link from "next/link";
import type { LucideIcon } from "lucide-react";
import { Menu, Server } from "lucide-react";

export interface SidebarNavItem {
  href: string;
  label: string;
  icon: LucideIcon;
  active?: boolean;
}

interface SidebarProps {
  items: SidebarNavItem[];
  backendUrl: string;
}

export function Sidebar({ items, backendUrl }: SidebarProps) {
  return (
    <aside className="hidden lg:flex lg:min-h-screen lg:flex-col lg:justify-between lg:border-r lg:border-slate-200/80 lg:bg-white/90 lg:px-4 lg:py-6 lg:backdrop-blur-xl">
      <div className="space-y-6">
        <div className="flex items-center gap-3 px-3">
          <button
            type="button"
            aria-label="Open navigation"
            className="flex h-10 w-10 items-center justify-center rounded-xl border border-slate-200 bg-slate-50 text-slate-500 shadow-sm"
          >
            <Menu className="h-5 w-5" />
          </button>
          <div>
            <p className="text-[1.75rem] font-bold tracking-tight text-blue-600">RegLoop AI</p>
            <p className="text-xs font-medium text-slate-500">Compliance Workspace</p>
          </div>
        </div>

        <nav className="space-y-1.5">
          {items.map((item) => {
            const Icon = item.icon;

            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={item.active ? "page" : undefined}
                className={`group flex items-center gap-3 rounded-2xl px-4 py-3 text-sm font-semibold transition-all ${
                  item.active
                    ? "bg-blue-50 text-blue-600 shadow-sm ring-1 ring-blue-100"
                    : "text-slate-600 hover:bg-slate-50 hover:text-slate-950"
                }`}
              >
                <span
                  className={`flex h-9 w-9 items-center justify-center rounded-xl border transition-colors ${
                    item.active
                      ? "border-blue-100 bg-white text-blue-600"
                      : "border-transparent bg-slate-100 text-slate-500 group-hover:border-slate-200 group-hover:bg-white"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                </span>
                <span>{item.label}</span>
              </Link>
            );
          })}
        </nav>
      </div>

      <div className="rounded-3xl border border-slate-200 bg-slate-50/80 p-4 shadow-sm">
        <div className="flex items-center gap-2 text-sm font-semibold text-slate-900">
          <span className="h-2.5 w-2.5 rounded-full bg-emerald-500 shadow-[0_0_0_4px_rgba(16,185,129,0.12)]" />
          API Status
        </div>
        <p className="mt-1 text-sm font-medium text-emerald-600">Connected</p>
        <div className="mt-4 flex items-start gap-3 rounded-2xl bg-white px-3 py-3 ring-1 ring-slate-200">
          <span className="mt-0.5 flex h-8 w-8 items-center justify-center rounded-xl bg-blue-50 text-blue-600">
            <Server className="h-4 w-4" />
          </span>
          <div className="min-w-0">
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Backend URL</p>
            <p className="truncate text-sm font-medium text-slate-700">{backendUrl}</p>
          </div>
        </div>
        <p className="mt-4 text-xs text-slate-500">Last checked: Just now</p>
      </div>
    </aside>
  );
}
