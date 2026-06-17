"use client";

import { CheckCircle2 } from "lucide-react";
import type { Obligation } from "@/types";
import { PRIORITY_CONFIG } from "@/constants/config";

interface ObligationTableProps {
  obligations: Obligation[] | null | undefined;
  isLoading?: boolean;
}

export function ObligationTable({ obligations, isLoading }: ObligationTableProps) {
  const obs = Array.isArray(obligations) ? obligations : [];

  if (isLoading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="h-14 animate-pulse rounded-2xl bg-slate-100" />
        ))}
      </div>
    );
  }

  if (obs.length === 0) {
    return (
      <div className="py-12 text-center text-slate-500">
        <div className="mb-3 inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 text-slate-400">
          <CheckCircle2 className="h-5 w-5" />
        </div>
        No obligations found
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[480px] text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-left">
            <th className="px-1 pb-3 text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-400">
              Priority
            </th>
            <th className="px-1 pb-3 text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-400">
              Category
            </th>
            <th className="px-1 pb-3 text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-400">
              Team
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {obs.slice(0, 5).map((ob, index) => {
            const priority = ob?.priority ?? "medium";
            const category = ob?.category ?? "Unknown";
            const team = ob?.responsible_team ?? "Unassigned";
            const priorityConfig =
              PRIORITY_CONFIG[priority as keyof typeof PRIORITY_CONFIG] || PRIORITY_CONFIG.medium;

            return (
              <tr
                key={ob?.id ?? `obligation-${index}`}
                className="group transition-colors duration-200 hover:bg-slate-50"
                style={{ animation: `fadeIn 0.45s ease-out ${index * 50}ms both` }}
              >
                <td className="px-1 py-4">
                  <span
                    className={`inline-flex items-center gap-2 rounded-full px-3 py-1.5 text-xs font-semibold whitespace-nowrap ${priorityConfig.badgeColor}`}
                  >
                    <span className="h-2 w-2 rounded-full" style={{ backgroundColor: priorityConfig.color }} />
                    {priorityConfig.label}
                  </span>
                </td>
                <td className="px-1 py-4 capitalize font-medium text-slate-700">{category}</td>
                <td className="px-1 py-4 text-slate-500">{team}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
