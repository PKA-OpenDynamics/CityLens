// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import Image from 'next/image';
import { 
  LayoutDashboard, 
  Users,
  Settings,
  LogOut,
  Circle,
  MapPin,
  Activity,
  AlertTriangle,
  BarChart3,
  Network,
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { useAuth } from '@/components/providers/auth-provider';

// Navigation - Data-Driven Intelligence Focus
const navigationGroups = [
  {
    title: 'Main',
    items: [
      { name: 'Dashboard', nameVi: 'Bảng điều khiển', href: '/dashboard', icon: LayoutDashboard },
      { name: 'Geographic Data', nameVi: 'Dữ liệu địa lý', href: '/geographic', icon: MapPin },
      { name: 'Reports', nameVi: 'Báo cáo sự cố', href: '/reports', icon: Circle },
    ],
  },
  {
    title: 'Data Intelligence',
    items: [
      { name: 'City Health Monitor', nameVi: 'Sức khỏe đô thị', href: '/admin/city-health', icon: Activity },
      { name: 'Data Insights', nameVi: 'Phân tích thông minh', href: '/admin/insights', icon: BarChart3 },
      { name: 'Smart Alerts', nameVi: 'Cảnh báo thông minh', href: '/admin/smart-alerts', icon: AlertTriangle },
      { name: 'LOD Cloud', nameVi: 'Mạng lưới dữ liệu mở', href: '/admin/lod-cloud', icon: Network },
    ],
  },
  {
    title: 'System',
    items: [
      { name: 'User Management', nameVi: 'Quản lý người dùng', href: '/admin/user-management', icon: Users },
      { name: 'Settings', nameVi: 'Cài đặt', href: '/settings', icon: Settings },
    ],
  },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { logout } = useAuth();

  const isActive = (href: string) => {
    return pathname === href || pathname.startsWith(href + '/');
  };

  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-72 border-r border-border/50 bg-gradient-to-b from-background via-background to-muted/20 dark:from-[#0a0a0a] dark:via-[#0f0f0f] dark:to-[#0a0a0a] shadow-2xl transition-all">
      {/* Gradient overlay for depth */}
      <div className="absolute inset-0 bg-gradient-to-br from-green-500/5 via-transparent to-green-600/10 dark:from-green-500/10 dark:via-transparent dark:to-green-600/5 pointer-events-none" />
      
      <div className="relative flex h-full flex-col">
        {/* Logo Section - Enhanced */}
        <div className="relative flex h-24 items-center border-b border-border/50 px-5 bg-gradient-to-r from-background via-background/95 to-background dark:from-[#0a0a0a] dark:via-[#0f0f0f] dark:to-[#0a0a0a] backdrop-blur-sm shrink-0">
          {/* Subtle accent line */}
          <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-green-500/40 to-transparent" />
          
          <div className="flex items-center gap-3 w-full">
            {/* Logo - Compact and elegant */}
            <div className="relative flex-shrink-0">
              <Image
                src="/CITYLENS.png"
                alt="CityLens Logo"
                width={64}
                height={64}
                className="w-14 h-14 object-contain rounded-lg"
                priority
              />
            </div>
            
            <div className="flex-1 min-w-0">
              <h1 className="text-lg font-bold tracking-tight text-foreground leading-tight">
                CITYLENS
              </h1>
              <p className="text-[10px] font-medium mt-0.5 text-muted-foreground flex items-center gap-1">
                <Circle className="h-1 w-1 fill-green-500 text-green-500" />
                <span className="truncate">Nền tảng Thành phố Thông minh</span>
              </p>
            </div>
          </div>
        </div>
        
        {/* Navigation - Enhanced with grouping */}
        <nav className="flex-1 overflow-y-auto custom-scrollbar">
          <div className="p-3 space-y-4">
            {navigationGroups.map((group, groupIndex) => (
              <div key={group.title} className={cn(groupIndex > 0 && 'pt-2')}>
                {/* Section Header */}
                <div className="px-3 mb-2">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground/60">
                    {group.title}
                  </h3>
                </div>
                
                {/* Menu Items */}
                <div className="space-y-1.5">
                  {group.items.map((item) => {
                    const active = isActive(item.href);
                    const Icon = item.icon;
                    
                    return (
                      <Link
                        key={item.name}
                        href={item.href}
                        className={cn(
                          'group relative flex items-center gap-3.5 rounded-lg px-3.5 py-3 transition-all duration-200',
                          'hover:bg-green-50 dark:hover:bg-green-950/20',
                          active
                            ? 'bg-gradient-to-r from-green-600 to-green-500 text-white shadow-lg shadow-green-500/30'
                            : 'text-muted-foreground hover:text-foreground'
                        )}
                      >
                        {/* Active indicator line */}
                        {active && (
                          <div className="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-white/90 rounded-r-full shadow-sm" />
                        )}
                        
                        {/* Icon */}
                        <Icon className={cn(
                          'h-5 w-5 flex-shrink-0 transition-all duration-200',
                          active 
                            ? 'text-white' 
                            : 'text-muted-foreground group-hover:text-green-600'
                        )} />
                        
                        {/* Text Content */}
                        <div className="flex-1 relative z-10 flex flex-col min-w-0 gap-1">
                          <span className={cn(
                            'text-sm font-semibold leading-tight truncate',
                            active ? 'text-white' : 'text-foreground group-hover:text-green-600'
                          )}>
                            {item.name}
                          </span>
                          <span className={cn(
                            'text-xs leading-tight truncate',
                            active 
                              ? 'text-white/90' 
                              : 'text-muted-foreground group-hover:text-foreground/75'
                          )}>
                            {item.nameVi}
                          </span>
                        </div>
                        
                        {/* Active indicator dot */}
                        {active && (
                          <span className="absolute right-3 h-2 w-2 rounded-full bg-white shadow-sm" />
                        )}
                      </Link>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </nav>
        
        {/* Footer - Enhanced */}
        <div className="mt-auto border-t border-border/50 p-4 bg-gradient-to-t from-muted/40 via-muted/20 to-transparent dark:from-[#0f0f0f] dark:via-[#0a0a0a] dark:to-transparent backdrop-blur-sm shrink-0">
          <div className="flex items-center gap-2.5">
            {/* Avatar */}
            <div className="relative flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-green-500/20 via-green-500/15 to-green-600/10 dark:from-green-500/30 dark:via-green-500/20 dark:to-green-600/10 border border-green-500/40 dark:border-green-500/50 shadow-sm">
              <Circle className="h-5 w-5 text-green-600 dark:text-green-500" />
              {/* Online indicator */}
              <span className="absolute bottom-0 right-0 h-2.5 w-2.5 rounded-full bg-green-500 border-2 border-background dark:border-[#0a0a0a] shadow-sm" />
            </div>
            
            <div className="flex-1 overflow-hidden min-w-0">
              <p className="truncate text-xs font-semibold text-foreground">Người dùng Admin</p>
              <p className="truncate text-[10px] text-muted-foreground mt-0.5">admin@citylens.vn</p>
              <span className="inline-flex items-center gap-1 text-[10px] font-medium text-green-600 dark:text-green-500 mt-1">
                <Circle className="h-1.5 w-1.5 fill-green-500 text-green-500" /> 
                <span>Đang hoạt động</span>
              </span>
            </div>
            
            <button 
              onClick={logout}
              className="ml-1 flex h-9 w-9 items-center justify-center rounded-lg bg-muted/60 hover:bg-green-600 hover:text-white border border-border/50 hover:border-green-500 transition-all duration-200 hover:scale-105 group" 
              title="Đăng xuất"
              aria-label="Đăng xuất"
            >
              <LogOut className="h-4 w-4 text-muted-foreground group-hover:text-white transition-colors" />
            </button>
          </div>
        </div>
      </div>
    </aside>
  );
}
