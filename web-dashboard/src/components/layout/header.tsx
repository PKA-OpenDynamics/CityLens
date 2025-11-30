// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

'use client';

import { Bell, Search, Moon, Sun } from 'lucide-react';
import { useTheme } from 'next-themes';
import { useEffect, useState } from 'react';
import { cn } from '@/lib/utils';

export default function Header() {
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <header className="sticky top-0 z-30 border-b border-border/50 bg-background/95 dark:bg-[#0a0a0a]/95 backdrop-blur-md shadow-sm">
      <div className="flex h-20 items-center justify-between px-6">
        {/* Search */}
        <div className="flex-1 max-w-2xl">
          <div className="relative group">
            <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-muted-foreground transition-colors group-focus-within:text-accent" />
            <input
              type="text"
              placeholder="Tìm kiếm địa điểm, báo cáo, phân tích..."
              className={cn(
                "w-full rounded-xl border border-border bg-card/80 dark:bg-card pl-12 pr-4 py-3",
                "text-sm placeholder:text-muted-foreground",
                "focus:outline-none focus:ring-2 focus:ring-accent/30 focus:border-accent",
                "transition-all duration-200 shadow-sm hover:shadow-md hover:border-accent/50"
              )}
            />
          </div>
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3">
          {/* Theme Toggle */}
          <button
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            className={cn(
              "flex h-11 w-11 items-center justify-center rounded-xl",
              "border border-border bg-card/80 dark:bg-card shadow-sm",
              "hover:bg-muted hover:border-accent hover:shadow-md hover:shadow-accent/20",
              "transition-all duration-200 hover:scale-105",
              "focus:outline-none focus:ring-2 focus:ring-accent/30"
            )}
            aria-label="Chuyển đổi giao diện sáng/tối"
            title={mounted ? (theme === 'dark' ? 'Chuyển sang sáng' : 'Chuyển sang tối') : 'Chuyển đổi giao diện'}
          >
            {mounted && theme === 'dark' ? (
              <Sun className="h-5 w-5 text-foreground" />
            ) : (
              <Moon className="h-5 w-5 text-foreground" />
            )}
          </button>

          {/* Notifications */}
          <button
            className={cn(
              "relative flex h-11 w-11 items-center justify-center rounded-xl",
              "border border-border bg-card/80 dark:bg-card shadow-sm",
              "hover:bg-muted hover:border-accent hover:shadow-md hover:shadow-accent/20",
              "transition-all duration-200 hover:scale-105",
              "focus:outline-none focus:ring-2 focus:ring-accent/30"
            )}
            aria-label="Thông báo"
            title="Thông báo"
          >
            <Bell className="h-5 w-5 text-foreground" />
            <span className="absolute right-2 top-2 flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-accent opacity-75"></span>
              <span className="relative inline-flex h-2 w-2 rounded-full bg-accent shadow-sm"></span>
            </span>
          </button>
        </div>
      </div>
    </header>
  );
}
