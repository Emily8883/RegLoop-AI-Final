"use client";

import { useState } from "react";
import { apiClient } from "@/services/api";

interface ExportButtonProps {
  onSuccess?: () => void;
  onError?: (error: string) => void;
}

export function ExportButton({ onSuccess, onError }: ExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false);
  const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

  const handleExport = async () => {
    setIsExporting(true);
    setMessage(null);

    try {
      const result = await apiClient.exportToCSV();

      if (result.success) {
        setMessage({ type: "success", text: "✓ Export successful! File downloaded." });
        onSuccess?.();

        // Clear message after 3 seconds
        setTimeout(() => setMessage(null), 3000);
      } else {
        const errorMsg = result.error || "Export failed";
        setMessage({ type: "error", text: `❌ ${errorMsg}` });
        onError?.(errorMsg);
      }
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : "Unknown error";
      setMessage({ type: "error", text: `❌ ${errorMsg}` });
      onError?.(errorMsg);
    } finally {
      setIsExporting(false);
    }
  };

  return (
    <div className="space-y-3">
      <button
        onClick={handleExport}
        disabled={isExporting}
        className={`
          inline-flex items-center gap-2 px-5 py-2.5 rounded-lg font-semibold transition-all duration-200
          ${isExporting
            ? "bg-slate-300 dark:bg-slate-700 text-slate-500 dark:text-slate-400 cursor-not-allowed"
            : "bg-blue-600 dark:bg-blue-700 text-white hover:bg-blue-700 dark:hover:bg-blue-600 active:scale-95 shadow-sm hover:shadow-md"
          }
        `}
        aria-label="Export compliance data as CSV"
      >
        <span className={isExporting ? "animate-spin" : ""}>📥</span>
        <span>{isExporting ? "Exporting..." : "Export CSV"}</span>
      </button>

      {message && (
        <div
          className={`
            animate-slideInUp text-sm font-medium p-3 rounded-lg
            ${
              message.type === "success"
                ? "bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300"
                : "bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300"
            }
          `}
        >
          {message.text}
        </div>
      )}
    </div>
  );
}
