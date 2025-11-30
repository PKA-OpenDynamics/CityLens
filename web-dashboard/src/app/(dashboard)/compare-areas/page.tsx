// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

'use client';

import { GitCompare } from 'lucide-react';

export default function CompareAreasPage() {
  return (
    <div className="animate-fade-in space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground flex items-center gap-3">
          <GitCompare className="h-8 w-8 text-accent" />
          Compare Areas
        </h1>
        <p className="mt-2 text-muted-foreground">
          So sánh dữ liệu giữa các khu vực
        </p>
      </div>

      <div className="rounded-xl border border-border bg-card p-12 text-center">
        <p className="text-muted-foreground">Trang này đang được phát triển...</p>
      </div>
    </div>
  );
}

