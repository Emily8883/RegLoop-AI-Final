"use client";

import { useState } from "react";
import { Download, FileJson2, FileSpreadsheet, FileText } from "lucide-react";
import { apiClient } from "@/services/api";

interface ExportButtonProps {
  documentId?: number;
  variant?: "primary" | "secondary" | "small";
}

export function ExportButton({ documentId, variant = "primary" }: ExportButtonProps) {
  const [isLoading, setIsLoading] = useState(false);
  const [showMenu, setShowMenu] = useState(false);

  const runExport = async (fn: () => Promise<{ success: boolean; error?: string }>) => {
    setIsLoading(true);
    try {
      const result = await fn();
      if (!result.success) {
        alert(result.error || "Export failed");
      }
    } finally {
      setIsLoading(false);
      setShowMenu(false);
    }
  };

  const baseStyles =
    "inline-flex items-center gap-3 rounded-lg border-2 font-bold transition-all duration-300 disabled:cursor-not-allowed disabled:opacity-50";
  const sizeStyles =
    variant === "small"
      ? "px-4 py-2 text-sm"
      : variant === "secondary"
        ? "px-6 py-3 text-base"
        : "px-8 py-4 text-lg";
  const colorStyles =
    variant === "secondary"
      ? "border-slate-300 bg-slate-100 text-slate-700 shadow-md hover:-translate-y-1 hover:border-slate-400 hover:bg-slate-200 hover:shadow-lg dark:border-slate-600 dark:bg-slate-800 dark:text-slate-300 dark:hover:border-slate-500 dark:hover:bg-slate-700"
      : "border-blue-500 bg-gradient-to-r from-blue-600 to-blue-700 text-white shadow-lg hover:-translate-y-1 hover:from-blue-700 hover:to-blue-800 hover:shadow-2xl dark:border-blue-600";

  if (variant === "small") {
    return (
      <button
        onClick={() => void runExport(() => apiClient.exportPackageJSON(documentId))}
        disabled={isLoading}
        className={`${baseStyles} ${sizeStyles} ${colorStyles}`}
      >
        <Download className="h-4 w-4" aria-hidden="true" />
        <span>{isLoading ? "Exporting..." : "Export"}</span>
      </button>
    );
  }

  return (
    <div className="relative inline-block">
      <button
        onClick={() => setShowMenu(!showMenu)}
        disabled={isLoading}
        className={`${baseStyles} ${sizeStyles} ${colorStyles}`}
      >
        <Download className="h-4 w-4" aria-hidden="true" />
        <span>{isLoading ? "Exporting..." : "Export Compliance Package"}</span>
      </button>

      {showMenu && (
        <div className="absolute right-0 z-50 mt-3 w-64 overflow-hidden rounded-xl border-2 border-slate-200 bg-white shadow-2xl dark:border-slate-700 dark:bg-slate-900">
          <button
            onClick={() => void runExport(() => apiClient.exportPackageJSON(documentId))}
            disabled={isLoading}
            className="w-full border-b-2 border-slate-200 px-6 py-4 text-left text-base font-semibold text-slate-700 transition-all duration-200 hover:border-blue-400 hover:bg-blue-50 dark:border-slate-700 dark:text-slate-200 dark:hover:border-blue-500 dark:hover:bg-blue-900/30"
          >
            <span className="inline-flex items-center gap-2">
              <FileJson2 className="h-4 w-4" aria-hidden="true" />
              JSON Format
            </span>
            <div className="mt-1 text-xs font-normal text-slate-500 dark:text-slate-400">
              Structured submission data
            </div>
          </button>
          <button
            onClick={() => void runExport(() => apiClient.exportTextReport(documentId))}
            disabled={isLoading}
            className="w-full border-b-2 border-slate-200 px-6 py-4 text-left text-base font-semibold text-slate-700 transition-all duration-200 hover:border-green-400 hover:bg-green-50 dark:border-slate-700 dark:text-slate-200 dark:hover:border-green-500 dark:hover:bg-green-900/30"
          >
            <span className="inline-flex items-center gap-2">
              <FileText className="h-4 w-4" aria-hidden="true" />
              Human Readable Text
            </span>
            <div className="mt-1 text-xs font-normal text-slate-500 dark:text-slate-400">
              Clean narrative export
            </div>
          </button>
          <button
            onClick={() => void runExport(() => apiClient.exportToCSV())}
            disabled={isLoading}
            className="w-full px-6 py-4 text-left text-base font-semibold text-slate-700 transition-all duration-200 hover:border-purple-400 hover:bg-purple-50 dark:text-slate-200 dark:hover:border-purple-500 dark:hover:bg-purple-900/30"
          >
            <span className="inline-flex items-center gap-2">
              <FileSpreadsheet className="h-4 w-4" aria-hidden="true" />
              CSV Format
            </span>
            <div className="mt-1 text-xs font-normal text-slate-500 dark:text-slate-400">
              Spreadsheet compatible
            </div>
          </button>
        </div>
      )}
    </div>
  );
}
