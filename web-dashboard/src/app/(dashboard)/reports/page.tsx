// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

'use client';

import { FileText, AlertCircle, CheckCircle, Clock } from 'lucide-react';

export default function ReportsPage() {
  return (
    <div className="animate-fade-in space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">Báo cáo</h1>
        <p className="mt-2 text-muted-foreground">
          Quản lý và theo dõi các báo cáo từ người dân
        </p>
      </div>

      {/* Stats Overview */}
      <div className="grid gap-4 md:grid-cols-4">
        <div className="rounded-xl border border-border bg-card p-6">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-500/10">
              <FileText className="h-6 w-6 text-blue-500" />
            </div>
            <div>
              <p className="text-2xl font-bold text-foreground">--</p>
              <p className="text-sm text-muted-foreground">Tổng báo cáo</p>
            </div>
          </div>
        </div>
        
        <div className="rounded-xl border border-border bg-card p-6">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-yellow-500/10">
              <Clock className="h-6 w-6 text-yellow-500" />
            </div>
            <div>
              <p className="text-2xl font-bold text-foreground">--</p>
              <p className="text-sm text-muted-foreground">Đang chờ</p>
            </div>
          </div>
        </div>
        
        <div className="rounded-xl border border-border bg-card p-6">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-orange-500/10">
              <AlertCircle className="h-6 w-6 text-orange-500" />
            </div>
            <div>
              <p className="text-2xl font-bold text-foreground">--</p>
              <p className="text-sm text-muted-foreground">Đang xử lý</p>
            </div>
          </div>
        </div>
        
        <div className="rounded-xl border border-border bg-card p-6">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-green-500/10">
              <CheckCircle className="h-6 w-6 text-green-500" />
            </div>
            <div>
              <p className="text-2xl font-bold text-foreground">--</p>
              <p className="text-sm text-muted-foreground">Đã giải quyết</p>
            </div>
          </div>
        </div>
      </div>

      {/* Placeholder content */}
      <div className="rounded-xl border border-border bg-card p-8 text-center">
        <FileText className="mx-auto h-12 w-12 text-muted-foreground/50" />
        <h3 className="mt-4 text-lg font-semibold text-foreground">
          Quản lý báo cáo
        </h3>
        <p className="mt-2 text-muted-foreground">
          Tính năng quản lý báo cáo chi tiết sẽ được phát triển trong giai đoạn tiếp theo.
        </p>
      </div>
    </div>
  );
}