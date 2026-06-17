"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
  BarChart3,
  CheckCircle2,
  FilePenLine,
  FileText,
  LayoutDashboard,
  ScrollText,
} from "lucide-react";
import { apiClient } from "@/services/api";
import { AppShell } from "@/components/layout/AppShell";
import { TopHeader } from "@/components/layout/TopHeader";
import { DashboardCards } from "@/components/DashboardCards";
import { ComplianceChart } from "@/components/ComplianceChart";
import { PriorityChart } from "@/components/PriorityChart";
import { DocumentTable } from "@/components/DocumentTable";
import { ObligationTable } from "@/components/ObligationTable";
import { ApiStatusCard } from "@/components/dashboard/ApiStatusCard";
import { QuickActionsCard } from "@/components/dashboard/QuickActionsCard";
import { ComplianceInfoCard } from "@/components/dashboard/ComplianceInfoCard";
import type { Document, Obligation, ComplianceSummary } from "@/types";

const BACKEND_URL = "http://127.0.0.1:8000";

export default function Dashboard() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [obligations, setObligations] = useState<Obligation[]>([]);
  const [complianceSummary, setComplianceSummary] = useState<ComplianceSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAllData = async () => {
      setIsLoading(true);
      setError(null);

      try {
        const [docsRes, oblsRes, complianceRes] = await Promise.all([
          apiClient.getDocuments(),
          apiClient.getObligations(),
          apiClient.getComplianceSummary(),
        ]);

        if (docsRes.error) {
          setError(docsRes.error);
        } else {
          setDocuments(docsRes.data.documents || []);
        }

        if (!oblsRes.error) {
          setObligations(oblsRes.data.obligations || []);
        }

        if (!complianceRes.error) {
          setComplianceSummary(complianceRes.data);
        }
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : "Unknown error";
        console.error("Fetch error:", errorMsg);
        setError("Failed to connect to backend. Ensure FastAPI server is running on http://127.0.0.1:8000");
      } finally {
        setIsLoading(false);
      }
    };

    fetchAllData();
  }, []);

  const navItems = useMemo(
    () => [
      { href: "/", label: "Dashboard", icon: LayoutDashboard, active: true },
      { href: "/documents", label: "Documents", icon: FileText },
      { href: "/obligations", label: "Obligations", icon: CheckCircle2 },
      { href: "/compliance", label: "Compliance", icon: BarChart3 },
      { href: "/policy-review", label: "Policy Review", icon: FilePenLine },
      { href: "/audit", label: "Audit Trail", icon: ScrollText },
    ],
    [],
  );

  const complianceScore = complianceSummary?.overall_compliance_score ?? 0;

  return (
    <AppShell sidebarItems={navItems} backendUrl={BACKEND_URL}>
      <div className="space-y-6">
        <TopHeader
          title="Dashboard"
          subtitle="Monitor regulatory documents, extracted obligations, compliance health, and operational risk."
        />

        <div className="overflow-x-auto lg:hidden">
          <div className="flex min-w-max gap-2 rounded-[24px] border border-slate-200/80 bg-white p-2 shadow-sm">
            {navItems.map((item) => {
              const Icon = item.icon;

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`inline-flex items-center gap-2 rounded-2xl px-4 py-2.5 text-sm font-semibold ${
                    item.active
                      ? "bg-blue-600 text-white shadow-sm"
                      : "text-slate-600 hover:bg-slate-50"
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  {item.label}
                </Link>
              );
            })}
          </div>
        </div>

        {error && !isLoading && (
          <div className="rounded-[24px] border border-red-200 bg-red-50 px-5 py-4 text-sm font-medium text-red-800 shadow-sm">
            {error}
          </div>
        )}

        <section className="rounded-[28px] border border-slate-200/80 bg-white px-5 py-5 shadow-sm sm:px-6">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div>
              <h1 className="text-[2rem] font-bold tracking-tight text-slate-950">
                Welcome to RegLoop AI
              </h1>
              <p className="mt-1 text-sm text-slate-600 sm:text-base">
                Overview of your compliance status and regulatory activities
              </p>
            </div>
            <div className="inline-flex items-center gap-2 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-medium text-slate-700 shadow-sm">
              <span className="h-2.5 w-2.5 rounded-full bg-emerald-500" />
              Live workspace healthy
            </div>
          </div>

          <div className="mt-6">
            <DashboardCards
              totalDocuments={documents.length}
              totalObligations={obligations.length}
              complianceData={complianceSummary}
              isLoading={isLoading}
            />
          </div>
        </section>

        <section className="grid gap-6 xl:grid-cols-[minmax(0,2fr)_minmax(360px,1fr)]">
          <div className="space-y-6">
            <div className="rounded-[28px] border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
              <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                  <div className="flex items-center gap-2 text-slate-950">
                    <span className="flex h-9 w-9 items-center justify-center rounded-2xl bg-blue-50 text-blue-600">
                      <BarChart3 className="h-4 w-4" />
                    </span>
                    <h2 className="text-lg font-semibold">Obligations by Category</h2>
                  </div>
                  <p className="mt-1 text-sm text-slate-500">
                    Distribution of obligations across compliance areas
                  </p>
                </div>
                <button
                  type="button"
                  className="inline-flex items-center rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2.5 text-sm font-medium text-slate-600 shadow-sm"
                >
                  This Month
                </button>
              </div>
              <ComplianceChart data={complianceSummary} isLoading={isLoading} />
            </div>

            <div className="grid gap-6 xl:grid-cols-2">
              <div className="rounded-[28px] border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
                <div className="mb-5 flex items-center justify-between gap-3">
                  <div>
                    <h2 className="text-lg font-semibold text-slate-950">Recent Documents</h2>
                    <p className="mt-1 text-sm text-slate-500">
                      Latest uploaded compliance source files
                    </p>
                  </div>
                  <Link href="/documents" className="text-sm font-semibold text-blue-600">
                    View all
                  </Link>
                </div>
                <DocumentTable documents={documents} isLoading={isLoading} />
              </div>

              <div className="rounded-[28px] border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
                <div className="mb-5 flex items-center justify-between gap-3">
                  <div>
                    <h2 className="text-lg font-semibold text-slate-950">Recent Obligations</h2>
                    <p className="mt-1 text-sm text-slate-500">
                      Current obligations grouped for fast review
                    </p>
                  </div>
                  <Link href="/obligations" className="text-sm font-semibold text-blue-600">
                    View all
                  </Link>
                </div>
                <ObligationTable obligations={obligations} isLoading={isLoading} />
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <div className="rounded-[28px] border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
              <div className="mb-5">
                <h2 className="text-lg font-semibold text-slate-950">Priority Breakdown</h2>
                <p className="mt-1 text-sm text-slate-500">
                  Current obligations grouped by priority
                </p>
              </div>
              <PriorityChart data={complianceSummary?.priority_breakdown} isLoading={isLoading} />
            </div>

            <ComplianceInfoCard
              obligationsCount={obligations.length}
              complianceScore={complianceScore}
            />
            <QuickActionsCard />
          </div>
        </section>

        <section className="rounded-[28px] border border-slate-200 bg-white p-5 shadow-sm sm:p-6">
          <div className="mb-4">
            <h2 className="text-lg font-semibold text-slate-950">Dashboard Health</h2>
            <p className="mt-1 text-sm text-slate-500">
              Keep track of backend connectivity and common next-step workflows without squeezing the main analytics area.
            </p>
          </div>
          <div className="grid gap-6 xl:grid-cols-[minmax(0,1.45fr)_minmax(320px,1fr)]">
            <ApiStatusCard backendUrl={BACKEND_URL} />
            <QuickActionsCard />
          </div>
        </section>
      </div>
    </AppShell>
  );
}
