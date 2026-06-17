"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/services/api";
import { ObligationTable } from "@/components/ObligationTable";
import { PRIORITY_CONFIG } from "@/constants/config";
import type { Obligation } from "@/types";

export default function ObligationsPage() {
  const [obligations, setObligations] = useState<Obligation[]>([]);
  const [filteredObligations, setFilteredObligations] = useState<Obligation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [priorityFilter, setPriorityFilter] = useState<string>("");
  const [categoryFilter, setCategoryFilter] = useState<string>("");

  useEffect(() => {
    const fetchObligations = async () => {
      setIsLoading(true);
      setError(null);

      const response = await apiClient.getObligations();

      if (response.error) {
        setError(response.error);
      } else {
        setObligations(response.data.obligations || []);
        setFilteredObligations(response.data.obligations || []);
      }

      setIsLoading(false);
    };

    fetchObligations();
  }, []);

  useEffect(() => {
    let filtered = obligations;

    if (priorityFilter) {
      filtered = filtered.filter((ob) => ob.priority === priorityFilter);
    }

    if (categoryFilter) {
      filtered = filtered.filter((ob) => ob.category === categoryFilter);
    }

    setFilteredObligations(filtered);
  }, [obligations, priorityFilter, categoryFilter]);

  const categories = useMemo(
    () => Array.from(new Set(obligations.map((ob) => ob.category))),
    [obligations],
  );

  return (
    <div className="page-shell bg-gradient-to-br from-slate-50 via-white to-green-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-800">
      <header className="sticky top-0 z-40 border-b border-slate-200/80 bg-white/95 shadow-sm backdrop-blur-xl dark:border-slate-700/80 dark:bg-slate-950/95">
        <div className="container-modern py-7">
          <Link
            href="/"
            className="mb-3 inline-flex items-center gap-2 text-sm font-medium text-slate-600 transition-colors hover:text-green-600 dark:text-slate-400 dark:hover:text-green-400"
          >
            ← <span>Back to Dashboard</span>
          </Link>
          <div className="space-y-2">
            <h1 className="flex items-center gap-3 text-4xl font-bold text-slate-900 dark:text-white">
              <span className="text-4xl">✓</span>
              <span>Obligations</span>
            </h1>
            <p className="text-slate-600 dark:text-slate-400">
              Track and manage regulatory obligations across all documents
            </p>
          </div>
        </div>
      </header>

      <main className="container-modern space-y-8 py-10">
        {error && !isLoading && (
          <div className="animate-slideInUp rounded-lg border-l-4 border-red-500 bg-red-50 p-5 shadow-md dark:bg-red-900/20">
            <div className="flex items-start gap-4">
              <span className="flex-shrink-0 text-2xl">⚠️</span>
              <div>
                <h3 className="font-semibold text-red-900 dark:text-red-200">
                  Error Loading Obligations
                </h3>
                <p className="mt-1 text-sm text-red-800 dark:text-red-300">{error}</p>
              </div>
            </div>
          </div>
        )}

        <section className="animate-slideInUp space-y-3">
          <h3 className="text-sm font-bold uppercase tracking-wide text-slate-900 dark:text-white">
            Filters
          </h3>
          <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
            <div>
              <label className="mb-3 block text-sm font-semibold text-slate-900 dark:text-white">
                <span className="flex items-center gap-2">
                  <span className="text-lg">🎯</span>
                  <span>Priority</span>
                </span>
              </label>
              <select
                value={priorityFilter}
                onChange={(e) => setPriorityFilter(e.target.value)}
                className="w-full rounded-lg border border-slate-200/80 bg-white px-4 py-3 text-slate-900 transition-all hover:border-slate-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 dark:border-slate-700/80 dark:bg-slate-800 dark:text-white dark:hover:border-slate-600 dark:focus:border-blue-400"
              >
                <option value="">All Priorities</option>
                <option value="high">🔴 High</option>
                <option value="medium">🟡 Medium</option>
                <option value="low">🟢 Low</option>
              </select>
            </div>

            <div>
              <label className="mb-3 block text-sm font-semibold text-slate-900 dark:text-white">
                <span className="flex items-center gap-2">
                  <span className="text-lg">📂</span>
                  <span>Category</span>
                </span>
              </label>
              <select
                value={categoryFilter}
                onChange={(e) => setCategoryFilter(e.target.value)}
                className="w-full rounded-lg border border-slate-200/80 bg-white px-4 py-3 text-slate-900 transition-all hover:border-slate-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 dark:border-slate-700/80 dark:bg-slate-800 dark:text-white dark:hover:border-slate-600 dark:focus:border-blue-400"
              >
                <option value="">All Categories</option>
                {categories.map((cat) => (
                  <option key={cat} value={cat}>
                    {cat.charAt(0).toUpperCase() + cat.slice(1)}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </section>

        <section className="overflow-hidden rounded-xl border border-slate-200/80 bg-white shadow-sm transition-all duration-300 hover:shadow-lg dark:border-slate-700/80 dark:bg-slate-900">
          <div className="border-b border-slate-200/80 bg-gradient-to-r from-slate-50/50 to-green-50/50 px-7 py-6 backdrop-blur-sm dark:border-slate-700/80 dark:from-slate-800/50 dark:to-slate-800/50">
            <div className="flex items-center justify-between">
              <div className="space-y-1">
                <h2 className="flex items-center gap-3 text-lg font-bold text-slate-900 dark:text-white">
                  <span className="text-xl">📋</span>
                  <span>All Obligations</span>
                </h2>
                <p className="text-sm text-slate-600 dark:text-slate-400">
                  Showing <span className="font-semibold text-slate-900 dark:text-white">{filteredObligations.length}</span> of{" "}
                  <span className="font-semibold text-slate-900 dark:text-white">{obligations.length}</span> obligations
                </p>
              </div>
            </div>
          </div>

          <div className="p-7">
            {isLoading ? (
              <div className="space-y-3">
                {[1, 2, 3, 4, 5].map((i) => (
                  <div
                    key={i}
                    className="h-14 animate-pulse rounded-md bg-slate-200 dark:bg-slate-700"
                  />
                ))}
              </div>
            ) : filteredObligations.length === 0 ? (
              <div className="py-16 text-center">
                <span className="mb-4 block text-5xl">📭</span>
                <p className="text-lg font-semibold text-slate-900 dark:text-white">No obligations found</p>
                <p className="mt-2 text-slate-600 dark:text-slate-400">
                  Upload and analyze documents to see obligations
                </p>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead className="border-b border-slate-200/80 bg-slate-50 dark:border-slate-700/80 dark:bg-slate-800/50">
                    <tr>
                      <th className="px-5 py-4 text-left font-semibold text-slate-700 dark:text-slate-300">
                        Priority
                      </th>
                      <th className="px-5 py-4 text-left font-semibold text-slate-700 dark:text-slate-300">
                        Category
                      </th>
                      <th className="px-5 py-4 text-left font-semibold text-slate-700 dark:text-slate-300">
                        Team
                      </th>
                      <th className="px-5 py-4 text-left font-semibold text-slate-700 dark:text-slate-300">
                        Description
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-200/80 dark:divide-slate-700/80">
                    {filteredObligations.map((ob, index) => (
                      <tr
                        key={ob.id}
                        className="animate-slideInUp transition-colors duration-200 hover:bg-slate-50 dark:hover:bg-slate-800/50"
                        style={{ animationDelay: `${index * 25}ms` }}
                      >
                        <td className="px-5 py-4">
                          <span
                            className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-bold ${
                              PRIORITY_CONFIG[ob.priority as keyof typeof PRIORITY_CONFIG].badgeColor
                            }`}
                          >
                            {PRIORITY_CONFIG[ob.priority as keyof typeof PRIORITY_CONFIG].label}
                          </span>
                        </td>
                        <td className="px-5 py-4 capitalize text-slate-600 dark:text-slate-400">
                          {ob.category}
                        </td>
                        <td className="px-5 py-4 text-slate-600 dark:text-slate-400">
                          {ob.responsible_team}
                        </td>
                        <td className="px-5 py-4 max-w-xs truncate text-slate-600 dark:text-slate-400">
                          {ob.obligation_text}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  );
}
