"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { apiClient } from "@/services/api";
import { DocumentTable } from "@/app/components/DocumentTable";
import type { Document } from "@/types";

interface MatrixState {
  filename: string;
  rowsLoaded: number;
  uploadedAt: string;
}

const MATRIX_STORAGE_KEY = "regloop-responsibility-matrix";

function formatDate(value?: string) {
  if (!value) {
    return "Not uploaded";
  }

  return new Date(value).toLocaleString();
}

export default function DocumentsPage() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [matrixState, setMatrixState] = useState<MatrixState | null>(null);

  const regulationInputRef = useRef<HTMLInputElement>(null);
  const policyInputRef = useRef<HTMLInputElement>(null);
  const matrixInputRef = useRef<HTMLInputElement>(null);

  const fetchDocuments = async () => {
    setIsLoading(true);
    setError(null);

    const response = await apiClient.getDocuments();
    if (response.error) {
      setError(response.error);
      setDocuments([]);
    } else {
      setDocuments(response.data.documents || []);
    }

    setIsLoading(false);
  };

  useEffect(() => {
    fetchDocuments();

    const storedMatrix = window.sessionStorage.getItem(MATRIX_STORAGE_KEY);
    if (storedMatrix) {
      try {
        setMatrixState(JSON.parse(storedMatrix));
      } catch {
        window.sessionStorage.removeItem(MATRIX_STORAGE_KEY);
      }
    }
  }, []);

  const regulationDocument = documents.find(
    (doc) => String(doc.document_type).toLowerCase() === "regulation"
  );
  const policyDocuments = documents.filter(
    (doc) => String(doc.document_type).toLowerCase() === "policy"
  );
  const otherDocuments = documents.filter((doc) => {
    const type = String(doc.document_type).toLowerCase();
    return type !== "regulation" && type !== "policy";
  });

  const canStartAnalysis =
    Boolean(regulationDocument) && policyDocuments.length >= 1 && policyDocuments.length <= 3 && Boolean(matrixState);

  const persistMatrixState = (value: MatrixState | null) => {
    setMatrixState(value);
    if (value) {
      window.sessionStorage.setItem(MATRIX_STORAGE_KEY, JSON.stringify(value));
    } else {
      window.sessionStorage.removeItem(MATRIX_STORAGE_KEY);
    }
  };

  const uploadDocument = async (
    file: File,
    documentType: "regulation" | "policy"
  ) => {
    setIsSubmitting(true);
    setError(null);
    setNotice(null);

    if (documentType === "policy" && policyDocuments.length >= 3) {
      setError("You can upload up to 3 policy documents in this workspace.");
      setIsSubmitting(false);
      return;
    }

    const existingRegulationId = documentType === "regulation" ? regulationDocument?.id : null;
    const response = await apiClient.uploadTypedDocument(file, documentType);

    if (response.error) {
      setError(response.error);
      setIsSubmitting(false);
      return;
    }

    if (existingRegulationId) {
      await apiClient.deleteDocument(existingRegulationId);
    }

    await fetchDocuments();
    setNotice(
      documentType === "regulation"
        ? "Regulation uploaded and workspace updated."
        : "Policy document uploaded successfully."
    );
    setIsSubmitting(false);
  };

  const uploadMatrix = async (file: File) => {
    setIsSubmitting(true);
    setError(null);
    setNotice(null);

    const response = await apiClient.uploadResponsibilityMatrix(file);
    if (response.error) {
      setError(response.error);
      setIsSubmitting(false);
      return;
    }

    persistMatrixState({
      filename: response.data.filename,
      rowsLoaded: response.data.rows_loaded,
      uploadedAt: new Date().toISOString(),
    });
    setNotice(`Responsibility matrix loaded with ${response.data.rows_loaded} assignments.`);
    setIsSubmitting(false);
  };

  const removeDocument = async (documentId: number) => {
    setIsSubmitting(true);
    setError(null);
    setNotice(null);

    const response = await apiClient.deleteDocument(documentId);
    if (response.error) {
      setError(response.error);
    } else {
      setNotice("Document removed from workspace.");
      await fetchDocuments();
    }

    setIsSubmitting(false);
  };

  const handleStartAnalysis = async () => {
    if (!regulationDocument) {
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setNotice(null);

    const response = await apiClient.analyzeDocument(regulationDocument.id);
    if (response.error) {
      setError(response.error);
    } else {
      setNotice(
        `Analysis complete: ${response.data.obligations_created} obligations extracted from ${regulationDocument.filename}.`
      );
      await fetchDocuments();
    }

    setIsAnalyzing(false);
  };

  return (
    <div className="page-shell bg-[radial-gradient(circle_at_top_left,_rgba(37,99,235,0.12),_transparent_30%),radial-gradient(circle_at_bottom_right,_rgba(16,185,129,0.10),_transparent_28%)] bg-slate-50 dark:bg-slate-950">
      <header className="sticky top-0 z-40 border-b border-slate-200/80 bg-white/95 shadow-sm backdrop-blur-xl dark:border-slate-800 dark:bg-slate-950/95">
        <div className="container-modern py-7">
          <Link
            href="/"
            className="mb-4 inline-flex items-center gap-2 text-sm font-semibold text-slate-600 transition-colors hover:text-blue-600 dark:text-slate-400 dark:hover:text-blue-400"
          >
            <span>Back to Dashboard</span>
          </Link>
          <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
            <div className="space-y-2">
              <h1 className="text-4xl font-bold text-slate-900 dark:text-white">Review Workspace</h1>
              <p className="max-w-3xl text-slate-600 dark:text-slate-400">
                Upload one regulation, one to three policy documents, and a responsibility matrix
                before starting analysis.
              </p>
            </div>
            <button
              onClick={() => void handleStartAnalysis()}
              disabled={!canStartAnalysis || isAnalyzing || isSubmitting}
              className="rounded-xl bg-blue-600 px-6 py-3 text-sm font-semibold text-white shadow-lg transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:bg-slate-300 dark:disabled:bg-slate-700"
            >
              {isAnalyzing ? "Running Analysis..." : "Start Analysis"}
            </button>
          </div>
        </div>
      </header>

      <main className="container-modern space-y-8 py-10">
        {(error || notice) && (
          <div
            className={`rounded-2xl border px-5 py-4 shadow-sm ${
              error
                ? "border-red-200 bg-red-50 text-red-800 dark:border-red-900/60 dark:bg-red-950/40 dark:text-red-200"
                : "border-green-200 bg-green-50 text-green-800 dark:border-green-900/60 dark:bg-green-950/40 dark:text-green-200"
            }`}
          >
            {error || notice}
          </div>
        )}

        <section className="grid gap-6 xl:grid-cols-[1.05fr_1.1fr_0.85fr]">
          <article className="rounded-3xl border border-slate-200/80 bg-white p-6 shadow-[0_24px_60px_-38px_rgba(15,23,42,0.45)] dark:border-slate-800 dark:bg-slate-900">
            <div className="mb-5 flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-blue-600 dark:text-blue-400">
                  Step 1
                </p>
                <h2 className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
                  Regulation Document
                </h2>
                <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
                  Upload the single regulatory update PDF that will drive extraction.
                </p>
              </div>
              <span className="rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-700 dark:bg-blue-900/40 dark:text-blue-200">
                Required
              </span>
            </div>

            <div className="space-y-4">
              <button
                onClick={() => regulationInputRef.current?.click()}
                disabled={isSubmitting}
                className="flex min-h-40 w-full flex-col items-center justify-center rounded-2xl border border-dashed border-blue-300 bg-blue-50/70 px-6 py-8 text-center transition hover:border-blue-500 hover:bg-blue-50 dark:border-blue-800 dark:bg-blue-950/20 dark:hover:border-blue-600"
              >
                <span className="text-sm font-semibold text-slate-900 dark:text-white">
                  {regulationDocument ? "Replace regulation PDF" : "Upload regulation PDF"}
                </span>
                <span className="mt-2 text-xs text-slate-500 dark:text-slate-400">
                  PDF only, used as the primary regulatory source
                </span>
              </button>
              <input
                ref={regulationInputRef}
                type="file"
                accept=".pdf"
                className="hidden"
                onChange={(event) => {
                  const file = event.target.files?.[0];
                  if (file) {
                    void uploadDocument(file, "regulation");
                  }
                  event.currentTarget.value = "";
                }}
              />

              {regulationDocument ? (
                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-950/60">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <p className="font-semibold text-slate-900 dark:text-white">{regulationDocument.filename}</p>
                      <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                        Uploaded {formatDate(regulationDocument.uploaded_at)}
                      </p>
                    </div>
                    <button
                      onClick={() => void removeDocument(regulationDocument.id)}
                      disabled={isSubmitting}
                      className="text-xs font-semibold text-red-600 transition hover:text-red-700 dark:text-red-400"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              ) : (
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  No regulation uploaded yet.
                </p>
              )}
            </div>
          </article>

          <article className="rounded-3xl border border-slate-200/80 bg-white p-6 shadow-[0_24px_60px_-38px_rgba(15,23,42,0.45)] dark:border-slate-800 dark:bg-slate-900">
            <div className="mb-5 flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-emerald-600 dark:text-emerald-400">
                  Step 2
                </p>
                <h2 className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">Internal Policies</h2>
                <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
                  Add one to three internal policy PDFs for mapping and gap review.
                </p>
              </div>
              <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-200">
                1-3 Required
              </span>
            </div>

            <div className="space-y-4">
              <button
                onClick={() => policyInputRef.current?.click()}
                disabled={isSubmitting || policyDocuments.length >= 3}
                className="flex min-h-32 w-full flex-col items-center justify-center rounded-2xl border border-dashed border-emerald-300 bg-emerald-50/70 px-6 py-8 text-center transition hover:border-emerald-500 hover:bg-emerald-50 disabled:cursor-not-allowed disabled:opacity-60 dark:border-emerald-800 dark:bg-emerald-950/20 dark:hover:border-emerald-600"
              >
                <span className="text-sm font-semibold text-slate-900 dark:text-white">Upload policy PDF</span>
                <span className="mt-2 text-xs text-slate-500 dark:text-slate-400">
                  {policyDocuments.length}/3 uploaded
                </span>
              </button>
              <input
                ref={policyInputRef}
                type="file"
                accept=".pdf"
                className="hidden"
                onChange={(event) => {
                  const file = event.target.files?.[0];
                  if (file) {
                    void uploadDocument(file, "policy");
                  }
                  event.currentTarget.value = "";
                }}
              />

              <div className="space-y-3">
                {policyDocuments.length === 0 ? (
                  <p className="text-sm text-slate-500 dark:text-slate-400">No policy files uploaded yet.</p>
                ) : (
                  policyDocuments.map((doc) => (
                    <div
                      key={doc.id}
                      className="flex items-start justify-between gap-4 rounded-2xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-950/60"
                    >
                      <div>
                        <p className="font-semibold text-slate-900 dark:text-white">{doc.filename}</p>
                        <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                          Uploaded {formatDate(doc.uploaded_at)}
                        </p>
                      </div>
                      <button
                        onClick={() => void removeDocument(doc.id)}
                        disabled={isSubmitting}
                        className="text-xs font-semibold text-red-600 transition hover:text-red-700 dark:text-red-400"
                      >
                        Remove
                      </button>
                    </div>
                  ))
                )}
              </div>
            </div>
          </article>

          <article className="rounded-3xl border border-slate-200/80 bg-white p-6 shadow-[0_24px_60px_-38px_rgba(15,23,42,0.45)] dark:border-slate-800 dark:bg-slate-900">
            <div className="mb-5 flex items-start justify-between gap-4">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-amber-600 dark:text-amber-400">
                  Step 3
                </p>
                <h2 className="mt-2 text-2xl font-bold text-slate-900 dark:text-white">
                  Responsibility Matrix
                </h2>
                <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
                  Upload the CSV mapping obligations to owners and teams.
                </p>
              </div>
              <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-700 dark:bg-amber-900/40 dark:text-amber-200">
                Required
              </span>
            </div>

            <div className="space-y-4">
              <button
                onClick={() => matrixInputRef.current?.click()}
                disabled={isSubmitting}
                className="flex min-h-32 w-full flex-col items-center justify-center rounded-2xl border border-dashed border-amber-300 bg-amber-50/70 px-6 py-8 text-center transition hover:border-amber-500 hover:bg-amber-50 dark:border-amber-800 dark:bg-amber-950/20 dark:hover:border-amber-600"
              >
                <span className="text-sm font-semibold text-slate-900 dark:text-white">
                  {matrixState ? "Replace matrix CSV" : "Upload matrix CSV"}
                </span>
                <span className="mt-2 text-xs text-slate-500 dark:text-slate-400">
                  Expected columns: `obligation_id`, `responsible_team`, `owner_email`
                </span>
              </button>
              <input
                ref={matrixInputRef}
                type="file"
                accept=".csv"
                className="hidden"
                onChange={(event) => {
                  const file = event.target.files?.[0];
                  if (file) {
                    void uploadMatrix(file);
                  }
                  event.currentTarget.value = "";
                }}
              />

              {matrixState ? (
                <div className="rounded-2xl border border-slate-200 bg-slate-50 p-4 dark:border-slate-800 dark:bg-slate-950/60">
                  <p className="font-semibold text-slate-900 dark:text-white">{matrixState.filename}</p>
                  <p className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                    {matrixState.rowsLoaded} rows loaded • {formatDate(matrixState.uploadedAt)}
                  </p>
                  <button
                    onClick={() => persistMatrixState(null)}
                    disabled={isSubmitting}
                    className="mt-3 text-xs font-semibold text-red-600 transition hover:text-red-700 dark:text-red-400"
                  >
                    Remove
                  </button>
                </div>
              ) : (
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  No responsibility matrix uploaded yet.
                </p>
              )}
            </div>
          </article>
        </section>

        <section className="grid gap-6 lg:grid-cols-[1.4fr_0.9fr]">
          <article className="rounded-3xl border border-slate-200/80 bg-white p-6 shadow-[0_24px_60px_-38px_rgba(15,23,42,0.45)] dark:border-slate-800 dark:bg-slate-900">
            <div className="mb-4">
              <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Workspace Validation</h2>
              <p className="mt-2 text-sm text-slate-600 dark:text-slate-400">
                Analysis unlocks only when the full challenge input set is present.
              </p>
            </div>
            <div className="grid gap-3 md:grid-cols-3">
              {[
                {
                  label: "Regulation uploaded",
                  ready: Boolean(regulationDocument),
                  helper: regulationDocument ? regulationDocument.filename : "Required",
                },
                {
                  label: "Policy set complete",
                  ready: policyDocuments.length >= 1 && policyDocuments.length <= 3,
                  helper:
                    policyDocuments.length === 0
                      ? "At least 1 policy required"
                      : `${policyDocuments.length} policy file(s) ready`,
                },
                {
                  label: "Matrix attached",
                  ready: Boolean(matrixState),
                  helper: matrixState ? `${matrixState.rowsLoaded} ownership rows loaded` : "CSV required",
                },
              ].map((item) => (
                <div
                  key={item.label}
                  className={`rounded-2xl border p-4 ${
                    item.ready
                      ? "border-green-200 bg-green-50 dark:border-green-900/70 dark:bg-green-950/30"
                      : "border-slate-200 bg-slate-50 dark:border-slate-800 dark:bg-slate-950/40"
                  }`}
                >
                  <p className="text-sm font-semibold text-slate-900 dark:text-white">{item.label}</p>
                  <p className="mt-2 text-xs text-slate-500 dark:text-slate-400">{item.helper}</p>
                </div>
              ))}
            </div>
          </article>

          <article className="rounded-3xl border border-slate-200/80 bg-white p-6 shadow-[0_24px_60px_-38px_rgba(15,23,42,0.45)] dark:border-slate-800 dark:bg-slate-900">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Workspace Summary</h2>
            <div className="mt-5 space-y-4">
              <div className="rounded-2xl bg-slate-50 p-4 dark:bg-slate-950/50">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                  Ready to analyze
                </p>
                <p className="mt-2 text-3xl font-bold text-slate-900 dark:text-white">
                  {canStartAnalysis ? "Yes" : "Not Yet"}
                </p>
              </div>
              <div className="rounded-2xl bg-slate-50 p-4 dark:bg-slate-950/50">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                  Uploaded artifacts
                </p>
                <p className="mt-2 text-3xl font-bold text-slate-900 dark:text-white">
                  {Number(Boolean(regulationDocument)) + policyDocuments.length + Number(Boolean(matrixState))}
                </p>
              </div>
              <div className="rounded-2xl bg-slate-50 p-4 dark:bg-slate-950/50">
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500 dark:text-slate-400">
                  Additional documents
                </p>
                <p className="mt-2 text-3xl font-bold text-slate-900 dark:text-white">{otherDocuments.length}</p>
              </div>
            </div>
          </article>
        </section>

        <section className="overflow-hidden rounded-3xl border border-slate-200/80 bg-white shadow-[0_24px_60px_-38px_rgba(15,23,42,0.45)] dark:border-slate-800 dark:bg-slate-900">
          <div className="border-b border-slate-200/80 px-8 py-6 dark:border-slate-800">
            <h2 className="text-2xl font-bold text-slate-900 dark:text-white">Uploaded Documents</h2>
            <p className="mt-1 text-sm text-slate-600 dark:text-slate-400">
              Current backend document inventory for this prototype workspace.
            </p>
          </div>
          <div className="p-8">
            <DocumentTable documents={documents} isLoading={isLoading} />
          </div>
        </section>
      </main>
    </div>
  );
}
