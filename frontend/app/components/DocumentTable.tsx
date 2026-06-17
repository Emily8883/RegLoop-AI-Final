"use client";

import type { Document } from "@/types";

interface DocumentTableProps {
  documents: Document[];
  isLoading?: boolean;
}

export function DocumentTable({ documents, isLoading = false }: DocumentTableProps) {
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3].map((i) => (
          <div
            key={i}
            className="flex items-center gap-5 p-5 bg-slate-100 dark:bg-slate-800 rounded-lg animate-pulse"
          >
            <div className="w-12 h-12 bg-slate-200 dark:bg-slate-700 rounded-lg" />
            <div className="flex-1 space-y-3">
              <div className="h-5 w-48 bg-slate-200 dark:bg-slate-700 rounded" />
              <div className="h-4 w-40 bg-slate-200 dark:bg-slate-700 rounded" />
            </div>
            <div className="h-8 w-16 bg-slate-200 dark:bg-slate-700 rounded" />
          </div>
        ))}
      </div>
    );
  }

  if (documents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <span className="text-5xl mb-4">📄</span>
        <p className="text-sm text-slate-600 dark:text-slate-400">
          No documents uploaded yet. Start by uploading a PDF file to analyze.
        </p>
      </div>
    );
  }

  const recentDocs = documents.slice(0, 5);

  return (
    <div className="space-y-3" role="region" aria-label="Recent documents list">
      {recentDocs.map((doc, index) => (
        <div
          key={doc.id}
          className="animate-slideInUp flex items-center justify-between gap-5 rounded-lg border-2 border-slate-200/70 dark:border-slate-700/70 bg-slate-50/60 dark:bg-slate-800/40 p-5 hover:bg-slate-100/80 dark:hover:bg-slate-800/70 hover:border-blue-400 dark:hover:border-blue-600 transition-all duration-200 shadow-md hover:shadow-lg"
          style={{ animationDelay: `${index * 50}ms` }}
          role="article"
          aria-label={`Document: ${doc.filename}`}
        >
          <div className="flex items-center gap-5 flex-1 min-w-0">
            <div className="flex-shrink-0 text-3xl" aria-hidden="true">
              📋
            </div>
            <div className="min-w-0 flex-1">
              <p className="font-bold text-slate-900 dark:text-white truncate text-sm">
                {doc.filename}
              </p>
              <p className="text-xs text-slate-600 dark:text-slate-400 mt-1.5">
                {new Date(doc.uploaded_at).toLocaleDateString()} •{" "}
                {(doc.text_length / 1024).toFixed(1)} KB
              </p>
            </div>
          </div>
          <div className="flex-shrink-0 text-right">
            <div
              className="inline-flex items-center gap-2.5 rounded-full bg-blue-100 dark:bg-blue-900/40 px-4 py-2 border border-blue-300 dark:border-blue-700 shadow-md"
              aria-label={`${doc.obligations_count} obligations found`}
            >
              <span className="text-lg" aria-hidden="true">
                ✓
              </span>
              <span className="text-sm font-bold text-blue-900 dark:text-blue-200">
                {doc.obligations_count}
              </span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
