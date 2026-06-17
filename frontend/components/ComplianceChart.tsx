"use client";

import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { ComplianceSummary } from "@/types";
import { CATEGORY_COLORS } from "@/constants/config";

interface ComplianceChartProps {
  data: ComplianceSummary | null;
  isLoading?: boolean;
}

export function ComplianceChart({ data, isLoading }: ComplianceChartProps) {
  if (isLoading) {
    return <div className="h-[280px] w-full animate-pulse rounded-[22px] bg-slate-100" />;
  }

  const categories = data?.categories;
  if (!categories || !Array.isArray(categories) || categories.length === 0) {
    return (
      <div className="flex h-[280px] w-full items-center justify-center rounded-[22px] bg-slate-50 text-slate-500">
        No obligation data available
      </div>
    );
  }

  const chartData = categories
    .filter((cat) => cat && cat.category)
    .map((cat) => ({
      name:
        (cat.category || "Unknown").charAt(0).toUpperCase() +
        (cat.category || "Unknown").slice(1),
      value: cat.total_obligations ?? 0,
      fill: CATEGORY_COLORS[cat.category?.toLowerCase()] || "#2563eb",
    }));

  return (
    <div className="h-[280px] w-full rounded-[22px] bg-slate-50/80 p-4 ring-1 ring-slate-100">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 12, right: 8, left: -18, bottom: 0 }}>
          <CartesianGrid vertical={false} strokeDasharray="4 4" stroke="#e2e8f0" />
          <XAxis
            dataKey="name"
            tickLine={false}
            axisLine={false}
            tick={{ fill: "#64748b", fontSize: 12, fontWeight: 500 }}
          />
          <YAxis
            tickLine={false}
            axisLine={false}
            tick={{ fill: "#94a3b8", fontSize: 12 }}
          />
          <Tooltip
            cursor={{ fill: "rgba(37,99,235,0.06)" }}
            contentStyle={{
              backgroundColor: "#ffffff",
              border: "1px solid #e2e8f0",
              borderRadius: "16px",
              boxShadow: "0 20px 40px rgba(15, 23, 42, 0.08)",
              color: "#0f172a",
            }}
          />
          <Bar dataKey="value" radius={[12, 12, 0, 0]} animationDuration={500} maxBarSize={56}>
            {chartData.map((entry) => (
              <Cell key={entry.name} fill={entry.fill} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
