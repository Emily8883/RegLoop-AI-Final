"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/services/api";
import { AuditTimeline } from "@/app/components/AuditTimeline";
import type { AuditTrailResponse, Document } from "@/types";

interface AuditEvent {
  timestamp: string;
  action: string;
  description: string;
  actor?: string;
  status?: "success" | "warning" | "error" | "info";
  details?: string;
}

function sortAuditDocuments(documents: Document[]): Document[] {
  return [...documents].sort((a, b) => {
    const aScore =
      (a.document_type?.toLowerCase() === "regulation" ? 100 : 0) +
      (a.obligations_count > 0 ? 10 : 0) +
      (a.uploaded_at ? 1 : 0);
    const bScore =
      (b.document_type?.toLowerCase() === "regulation" ? 100 : 0) +
      (b.obligations_count > 0 ? 10 : 0) +
      (b.uploaded_at ? 1 : 0);

    if (aScore !== bScore) {
      return bScore - aScore;
    }

    return b.id - a.id;
  });
}

function buildEvents(auditTrail: AuditTrailResponse | null): AuditEvent[] {
  if (!auditTrail) {
    return [];
  }

  const events: AuditEvent[] = [
    {
      timestamp: auditTrail.document_uploaded_at || new Date().toISOString(),
      action: "Document Uploaded",
      description: `${auditTrail.document_name} entered the review workspace.`,
      actor: "System",
      status: "success",
    },
  ];

  auditTrail.obligations.forEach((obligation) => {
    events.push({
      timestamp: obligation.extracted_at || new Date().toISOString(),
      action: "Obligation Extracted",
      description: obligation.obligation_text,
      actor: "AI Extraction",
      status: "info",
      details: `Citation: ${obligation.source_citation || "N/A"} | Priority: ${obligation.priority} | Category: ${obligation.category}`,
    });

    if (obligation.gap_analysis) {
      events.push({
        timestamp: obligation.gap_analysis.created_at || new Date().toISOString(),
        action: "Gap Assessed",
        description: obligation.gap_analysis.gap_summary || "Gap analysis recorded.",
        actor: "Compliance Engine",
        status: obligation.gap_analysis.coverage_score >= 70 ? "success" : "warning",
        details: `Coverage: ${obligation.gap_analysis.coverage_score}% | Recommendation: ${obligation.gap_analysis.recommended_action || "N/A"}`,
      });
    }

    if (obligation.policy_pr) {
      events.push({
        timestamp: obligation.policy_pr.created_at || new Date().toISOString(),
        action: "Policy Pull Request Generated",
        description: `PR #${obligation.policy_pr.id} created for this obligation.`,
        actor: "Policy Generator",
        status: "success",
        details: `Risk: ${obligation.policy_pr.risk_level} | Status: ${obligation.policy_pr.status} | Proposed amendment: ${obligation.policy_pr.proposed_amendment}`,
      });
    }

    obligation.review_history.forEach((review) => {
      events.push({
        timestamp: review.timestamp || new Date().toISOString(),
        action: `Review Action: ${review.action}`,
        description: review.comments || "Reviewer action recorded.",
        actor: review.reviewer || "Reviewer",
        status: review.action === "approve" ? "success" : review.action === "reject" ? "error" : "warning",
      });
    });
  });

  return events.sort(
    (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  );
}

export default function AuditPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocId, setSelectedDocId] = useState<number | null>(null);
  const [auditTrail, setAuditTrail] = useState<AuditTrailResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDocuments = async () => {
      setIsLoading(true);
      const response = await apiClient.getDocuments();

      if (response.error) {
        setError(response.error);
        setDocuments([]);
      } else {
        const docs = sortAuditDocuments(response.data.documents || []);
        setDocuments(docs);
        if (docs.length > 0) {
          const defaultDoc =
            docs.find((doc) => doc.document_type?.toLowerCase() === "regulation" && doc.obligations_count > 0) ||
            docs.find((doc) => doc.document_type?.toLowerCase() === "regulation") ||
            docs.find((doc) => doc.obligations_count > 0) ||
            docs[0];
          setSelectedDocId(defaultDoc.id);
        }
      }

      setIsLoading(false);
    };

    fetchDocuments();
  }, []);

  useEffect(() => {
    if (!selectedDocId) {
      return;
    }

    const fetchAuditTrail = async () => {
      setIsLoading(true);
      const response = await apiClient.getAuditTrail(selectedDocId);

      if (response.error) {
        setError(response.error);
        setAuditTrail(null);
      } else {
        setError(null);
        setAuditTrail(response.data);
      }

      setIsLoading(false);
    };

    fetchAuditTrail();
  }, [selectedDocId]);

  const auditEvents = buildEvents(auditTrail);

  return (
    <div className="page-shell bg-gradient-to-br from-slate-50 via-white to-indigo-50 dark:from-slate-950 dark:via-slate-900 dark:to-slate-800">
      <header className="sticky top-0 z-40 border-b border-slate-200/80 bg-white/95 shadow-sm backdrop-blur-xl dark:border-slate-700/80 dark:bg-slate-950/95">
        <div className="container-modern py-7">
          <Link
            href="/"
            className="mb-3 inline-flex items-center gap-2 text-sm font-medium text-slate-600 transition-colors hover:text-blue-600 dark:text-slate-400 dark:hover:text-blue-400"
          >
            <span>Back to Dashboard</span>
          </Link>
          <div className="space-y-2">
            <h1 className="text-4xl font-bold text-slate-900 dark:text-white">Audit Trail</h1>
            <p className="text-sm text-slate-600 dark:text-slate-400">
              End-to-end traceability from uploaded regulation to final review action.
            </p>
          </div>
        </div>
      </header>

      <main className="container-modern space-y-8 py-8">
        {error && (
          <div className="rounded-lg border border-red-200 bg-red-50 p-4 shadow-sm dark:border-red-800 dark:bg-red-900/20">
            <p className="text-sm font-medium text-red-800 dark:text-red-200">{error}</p>
          </div>
        )}

        <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
          <h2 className="mb-4 text-lg font-bold text-slate-900 dark:text-white">Select Document</h2>

          {isLoading && documents.length === 0 ? (
            <div className="flex h-20 items-center justify-center">
              <div className="mx-auto h-6 w-6 animate-spin rounded-full border-b-2 border-blue-600" />
            </div>
          ) : documents.length === 0 ? (
            <div className="py-8 text-center text-slate-500 dark:text-slate-400">
              No documents available. Upload and analyze a document first.
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-3 md:grid-cols-2 lg:grid-cols-3">
              {documents.map((doc) => (
                <button
                  key={doc.id}
                  onClick={() => setSelectedDocId(doc.id)}
                  className={`rounded-lg border-2 p-3 text-left transition-all ${
                    selectedDocId === doc.id
                      ? "border-blue-600 bg-blue-50 dark:bg-blue-900/20"
                      : "border-slate-200 bg-slate-50 hover:border-slate-300 dark:border-slate-700 dark:bg-slate-800 dark:hover:border-slate-600"
                  }`}
                >
                  <div className="text-sm font-semibold text-slate-900 dark:text-white">{doc.filename}</div>
                  <div className="mt-1 text-xs text-slate-600 dark:text-slate-400">
                    ID {doc.id} • {doc.document_type?.toUpperCase?.() || "UNKNOWN"} • {doc.text_length} characters
                  </div>
                  <div className="mt-1 text-[11px] text-slate-500 dark:text-slate-500">
                    Obligations: {doc.obligations_count}
                  </div>
                </button>
              ))}
            </div>
          )}
        </div>

        {selectedDocId && (
          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <div>
                <h2 className="text-lg font-bold text-slate-900 dark:text-white">Processing Timeline</h2>
                {auditTrail && (
                  <p className="text-sm text-slate-500 dark:text-slate-400">
                    Showing document ID {auditTrail.document_id}: {auditTrail.document_name}
                  </p>
                )}
              </div>
              <button
                onClick={() => void (selectedDocId ? apiClient.getAuditTrail(selectedDocId).then((response) => {
                  if (response.error) {
                    setError(response.error);
                    setAuditTrail(null);
                  } else {
                    setError(null);
                    setAuditTrail(response.data);
                  }
                }) : Promise.resolve())}
                className="rounded-lg border border-slate-300 bg-white px-4 py-2 text-sm font-medium text-slate-700 transition-colors hover:bg-slate-50 dark:border-slate-600 dark:bg-slate-800 dark:text-slate-200 dark:hover:bg-slate-700"
              >
                Refresh audit trail
              </button>
            </div>
            <AuditTimeline events={auditEvents} isLoading={isLoading} title="" />
          </div>
        )}

        {auditTrail && (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
            <div className="rounded-lg border border-blue-200 bg-blue-50 p-4 dark:border-blue-800 dark:bg-blue-900/20">
              <p className="text-xs font-semibold uppercase text-blue-700 dark:text-blue-300">Obligations</p>
              <p className="mt-2 text-2xl font-bold text-blue-600 dark:text-blue-400">{auditTrail.obligations.length}</p>
            </div>
            <div className="rounded-lg border border-yellow-200 bg-yellow-50 p-4 dark:border-yellow-800 dark:bg-yellow-900/20">
              <p className="text-xs font-semibold uppercase text-yellow-700 dark:text-yellow-300">Open Gaps</p>
              <p className="mt-2 text-2xl font-bold text-yellow-600 dark:text-yellow-400">
                {auditTrail.obligations.filter((item) => item.gap_analysis).length}
              </p>
            </div>
            <div className="rounded-lg border border-purple-200 bg-purple-50 p-4 dark:border-purple-800 dark:bg-purple-900/20">
              <p className="text-xs font-semibold uppercase text-purple-700 dark:text-purple-300">Policy PRs</p>
              <p className="mt-2 text-2xl font-bold text-purple-600 dark:text-purple-400">
                {auditTrail.obligations.filter((item) => item.policy_pr).length}
              </p>
            </div>
            <div className="rounded-lg border border-green-200 bg-green-50 p-4 dark:border-green-800 dark:bg-green-900/20">
              <p className="text-xs font-semibold uppercase text-green-700 dark:text-green-300">Review Actions</p>
              <p className="mt-2 text-2xl font-bold text-green-600 dark:text-green-400">
                {auditTrail.obligations.reduce((sum, item) => sum + item.review_history.length, 0)}
              </p>
            </div>
          </div>
        )}

        {selectedDocId && (
          <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-700 dark:bg-slate-900">
            <h2 className="mb-4 text-lg font-bold text-slate-900 dark:text-white">Export Audit Report</h2>
            <p className="mb-4 text-sm text-slate-600 dark:text-slate-400">
              Download the current document package in submission-ready formats.
            </p>
            <div className="flex flex-wrap gap-3">
              <button
                onClick={() => void apiClient.exportPackageJSON(selectedDocId)}
                className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-blue-700"
              >
                Download JSON
              </button>
              <button
                onClick={() => void apiClient.exportToCSV()}
                className="rounded-lg bg-green-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-green-700"
              >
                Download CSV
              </button>
              <button
                onClick={() => void apiClient.exportTextReport(selectedDocId)}
                className="rounded-lg bg-slate-700 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-slate-800"
              >
                Download Text Summary
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
