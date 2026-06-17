"use client";

import { FileText } from "lucide-react";
import type { Document } from "@/types";

interface DocumentTableProps {
  documents: Document[] | null | undefined;
  isLoading?: boolean;
}

export function DocumentTable({ documents, isLoading }: DocumentTableProps) {
  const docs = Array.isArray(documents) ? documents : [];

  if (isLoading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="h-14 animate-pulse rounded-2xl bg-slate-100" />
        ))}
      </div>
    );
  }

  if (docs.length === 0) {
    return (
      <div className="py-12 text-center text-slate-500">
        <div className="mb-3 inline-flex h-12 w-12 items-center justify-center rounded-2xl bg-slate-100 text-slate-400">
          <FileText className="h-5 w-5" />
        </div>
        No documents uploaded yet
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <table className="w-full min-w-[520px] text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-left">
            <th className="px-1 pb-3 text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-400">
              Document
            </th>
            <th className="px-1 pb-3 text-center text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-400">
              Obligations
            </th>
            <th className="px-1 pb-3 text-right text-[11px] font-semibold uppercase tracking-[0.18em] text-slate-400">
              Uploaded
            </th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-100">
          {docs.slice(0, 5).map((doc, index) => {
            const fileName = doc?.filename ?? "Unknown";
            const obligationsCount = doc?.obligations_count ?? 0;
            const uploadedDate = doc?.uploaded_at
              ? new Date(doc.uploaded_at).toLocaleDateString("en-US", {
                  month: "short",
                  day: "numeric",
                  year: "numeric",
                })
              : "Unknown";

            return (
              <tr
                key={doc?.id ?? `document-${index}`}
                className="group transition-colors duration-200 hover:bg-slate-50"
                style={{ animation: `fadeIn 0.45s ease-out ${index * 50}ms both` }}
              >
                <td className="px-1 py-4">
                  <div className="flex items-center gap-3">
                    <span className="flex h-9 w-9 items-center justify-center rounded-xl bg-blue-50 text-blue-600 ring-1 ring-blue-100">
                      <FileText className="h-4 w-4" />
                    </span>
                    <div className="min-w-0">
                      <p className="truncate font-medium text-slate-900" title={fileName}>
                        {fileName}
                      </p>
                    </div>
                  </div>
                </td>
                <td className="px-1 py-4 text-center">
                  <span className="inline-flex min-w-8 items-center justify-center rounded-full bg-blue-100 px-2.5 py-1 text-xs font-semibold text-blue-700">
                    {obligationsCount}
                  </span>
                </td>
                <td className="px-1 py-4 text-right text-sm font-medium text-slate-500">
                  {uploadedDate}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
