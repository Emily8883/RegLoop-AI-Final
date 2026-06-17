"use client";

interface AuditEvent {
  timestamp: string;
  action: string;
  description: string;
  actor?: string;
  status?: "success" | "warning" | "error" | "info";
  details?: string;
}

interface AuditTimelineProps {
  events: AuditEvent[];
  isLoading?: boolean;
  title?: string;
}

const STATUS_ICONS = {
  success: "✅",
  warning: "⚠️",
  error: "❌",
  info: "ℹ️",
};

const STATUS_COLORS = {
  success: "bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 border-green-300 dark:border-green-700",
  warning: "bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 border-yellow-300 dark:border-yellow-700",
  error: "bg-red-100 dark:bg-red-900 text-red-800 dark:text-red-200 border-red-300 dark:border-red-700",
  info: "bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 border-blue-300 dark:border-blue-700",
};

function formatDate(dateString: string): string {
  try {
    const date = new Date(dateString);
    return date.toLocaleString("en-US", {
      month: "short",
      day: "numeric",
      year: "numeric",
      hour: "2-digit",
      minute: "2-digit",
      second: "2-digit",
    });
  } catch {
    return dateString;
  }
}

export function AuditTimeline({ events, isLoading = false, title = "Audit Trail" }: AuditTimelineProps) {
  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-48">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-3"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading audit trail...</p>
        </div>
      </div>
    );
  }

  if (!events || events.length === 0) {
    return (
      <div className="text-center py-12 border border-dashed border-gray-300 dark:border-gray-700 rounded-lg">
        <span className="text-4xl mb-3 block">📋</span>
        <p className="text-gray-600 dark:text-gray-400 font-medium">No events recorded</p>
        <p className="text-sm text-gray-500 dark:text-gray-500 mt-1">Audit trail will appear here as actions occur</p>
      </div>
    );
  }

  return (
    <div>
      <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-6">{title}</h3>
      <div className="relative">
        {/* Timeline line */}
        <div className="absolute left-8 top-0 bottom-0 w-1 bg-gray-200 dark:bg-gray-700"></div>

        {/* Events */}
        <div className="space-y-6">
          {events.map((event, index) => {
            const status = (event.status || "info") as keyof typeof STATUS_COLORS;
            const icon = STATUS_ICONS[status];
            const colorClass = STATUS_COLORS[status];

            return (
              <div key={index} className="relative pl-24">
                {/* Timeline dot */}
                <div className="absolute left-2 top-1 w-12 h-12 bg-white dark:bg-gray-900 border-4 border-gray-200 dark:border-gray-700 rounded-full flex items-center justify-center text-lg z-10">
                  {icon}
                </div>

                {/* Event card */}
                <div className={`p-4 rounded-lg border ${colorClass} shadow-sm`}>
                  <div className="flex items-start justify-between mb-2">
                    <div>
                      <h4 className="font-semibold text-sm mb-1">{event.action}</h4>
                      <p className="text-xs text-gray-700 dark:text-gray-300">{formatDate(event.timestamp)}</p>
                    </div>
                    {event.actor && <span className="text-xs font-medium bg-white dark:bg-gray-800 px-2 py-1 rounded">{event.actor}</span>}
                  </div>
                  <p className="text-sm mb-2">{event.description}</p>
                  {event.details && (
                    <details className="text-xs text-gray-700 dark:text-gray-300 cursor-pointer">
                      <summary className="font-medium mb-2">View Details</summary>
                      <pre className="bg-white dark:bg-gray-800 p-2 rounded mt-2 overflow-x-auto text-xs">
                        {event.details}
                      </pre>
                    </details>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
