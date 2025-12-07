// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

'use client';

import { Bell, Shield, Database, Palette } from 'lucide-react';

export default function SettingsPage() {
  return (
    <div className="animate-fade-in space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">Cài đặt</h1>
        <p className="mt-2 text-muted-foreground">
          Quản lý cấu hình và tùy chỉnh hệ thống
        </p>
      </div>

      {/* Settings Cards */}
      <div className="grid gap-6 md:grid-cols-2">
        <div className="rounded-xl border border-border bg-card p-6 hover-lift">
          <div className="flex items-start gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-accent/10">
              <Bell className="h-6 w-6 text-accent" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-foreground">Thông báo</h3>
              <p className="mt-1 text-sm text-muted-foreground">
                Cấu hình thông báo và cảnh báo hệ thống
              </p>
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-border bg-card p-6 hover-lift">
          <div className="flex items-start gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-accent/10">
              <Shield className="h-6 w-6 text-accent" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-foreground">Bảo mật</h3>
              <p className="mt-1 text-sm text-muted-foreground">
                Quản lý bảo mật và quyền truy cập
              </p>
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-border bg-card p-6 hover-lift">
          <div className="flex items-start gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-accent/10">
              <Database className="h-6 w-6 text-accent" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-foreground">Dữ liệu</h3>
              <p className="mt-1 text-sm text-muted-foreground">
                Cấu hình nguồn dữ liệu và đồng bộ
              </p>
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-border bg-card p-6 hover-lift">
          <div className="flex items-start gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-accent/10">
              <Palette className="h-6 w-6 text-accent" />
            </div>
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-foreground">Giao diện</h3>
              <p className="mt-1 text-sm text-muted-foreground">
                Tùy chỉnh màu sắc và hiển thị
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
