export interface Document {
  id: string;
  title: string;
  uploaded_at?: string;
}

export interface Obligation {
  id: string;
  title: string;
  status?: string;
}

export interface ComplianceSummary {
  total: number;
  compliant: number;
  non_compliant: number;
}

export async function fetchDocuments(): Promise<Document[]> {
  return [];
}

export async function fetchObligations(): Promise<Obligation[]> {
  return [];
}

export async function fetchComplianceSummary(): Promise<ComplianceSummary> {
  return {
    total: 0,
    compliant: 0,
    non_compliant: 0,
  };
}

export function formatDate(date: string) {
  return new Date(date).toLocaleDateString();
}

export function truncateText(text: string, length = 100) {
  return text.length > length
    ? text.slice(0, length) + "..."
    : text;
}