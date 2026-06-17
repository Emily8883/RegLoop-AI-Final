"use client";

import type { ReactNode } from "react";
import { Sidebar, type SidebarNavItem } from "@/components/layout/Sidebar";

interface AppShellProps {
  sidebarItems: SidebarNavItem[];
  backendUrl: string;
  children: ReactNode;
}

export function AppShell({ sidebarItems, backendUrl, children }: AppShellProps) {
  return (
    <div className="bg-[linear-gradient(180deg,#f8fbff_0%,#f6f8fc_52%,#f8fafc_100%)]">
      <div className="app-shell-grid">
        <Sidebar items={sidebarItems} backendUrl={backendUrl} />
        <div className="main-area relative flex min-h-screen flex-col overflow-hidden">
          <div className="pointer-events-none absolute inset-x-0 top-0 h-72 bg-[radial-gradient(circle_at_top_left,rgba(37,99,235,0.10),transparent_38%),radial-gradient(circle_at_top_right,rgba(79,70,229,0.08),transparent_30%)]" />
          <div className="dashboard-container relative flex-1">{children}</div>
        </div>
      </div>
    </div>
  );
}
