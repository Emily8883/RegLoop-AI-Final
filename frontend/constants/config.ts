/**
 * Central configuration file for RegLoop AI Frontend
 * API Base URL and other configuration constants
 */

export const API_BASE_URL = "http://127.0.0.1:8000";

/**
 * API Endpoints
 */
export const API_ENDPOINTS = {
  DOCUMENTS: "/documents",
  OBLIGATIONS: "/obligations",
  COMPLIANCE_SUMMARY: "/compliance-summary",
  UPLOAD: "/upload",
  RESPONSIBILITY_MATRIX: "/upload/responsibility-matrix",
  ANALYZE: (documentId: number) => `/documents/${documentId}/analyze`,
  ANALYZE_WITH_GAPS: (documentId: number) => `/documents/${documentId}/analyze-and-gaps`,
  DELETE_DOCUMENT: (documentId: number) => `/documents/${documentId}`,
} as const;

/**
 * Priority levels and their display properties
 */
export const PRIORITY_CONFIG = {
  high: {
    label: "High",
    color: "#ef4444",
    bgColor: "bg-red-50 dark:bg-red-900/20",
    badgeColor: "bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-200",
  },
  medium: {
    label: "Medium",
    color: "#f59e0b",
    bgColor: "bg-amber-50 dark:bg-amber-900/20",
    badgeColor: "bg-amber-100 dark:bg-amber-900/30 text-amber-800 dark:text-amber-200",
  },
  low: {
    label: "Low",
    color: "#10b981",
    bgColor: "bg-green-50 dark:bg-green-900/20",
    badgeColor: "bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-200",
  },
} as const;

/**
 * Category colors for charts
 */
export const CATEGORY_COLORS: Record<string, string> = {
  operational: "#3b82f6",
  reporting: "#f59e0b",
  security: "#ef4444",
  compliance: "#8b5cf6",
} as const;
