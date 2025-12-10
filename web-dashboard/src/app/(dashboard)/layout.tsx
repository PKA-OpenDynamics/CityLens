// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import Sidebar from '@/components/layout/sidebar';
import Header from '@/components/layout/header';
import { ProtectedRoute } from '@/components/providers/protected-route';

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <ProtectedRoute>
      <div className="flex min-h-screen bg-gradient-to-br from-background via-background to-muted/20 dark:from-[#0a0a0a] dark:via-[#0f0f0f] dark:to-[#0a0a0a]">
        <Sidebar />
        <div className="ml-72 flex-1 flex flex-col min-w-0">
          <Header />
          <main className="flex-1 p-6 custom-scrollbar overflow-auto bg-gradient-to-br from-background/50 via-background to-background dark:from-[#0a0a0a]/50 dark:via-[#0f0f0f] dark:to-[#0a0a0a]">
            {children}
          </main>
        </div>
      </div>
    </ProtectedRoute>
  );
}
