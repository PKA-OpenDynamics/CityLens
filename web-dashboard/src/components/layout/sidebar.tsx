// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  LayoutDashboard, 
  Map, 
  BarChart3, 
  FileText,
  Users,
  Settings,
  Info,
  LogOut,
  Circle
} from 'lucide-react';
import { cn } from '@/lib/utils';

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Bản đồ', href: '/map', icon: Map },
  { name: 'Phân tích', href: '/analytics', icon: BarChart3 },
  { name: 'Báo cáo', href: '/reports', icon: FileText },
  { name: 'Người dùng', href: '/users', icon: Users },
  { name: 'Cài đặt', href: '/settings', icon: Settings },
  { name: 'Giới thiệu', href: '/about', icon: Info },
];

export default function Sidebar() {
  const pathname = usePathname();
  return (
    <aside className="fixed left-0 top-0 z-40 h-screen w-72 bg-gradient-to-br from-[#101c2c] via-[#1a2a3a] to-[#1a1a1a] shadow-2xl transition-all">
      <div className="flex h-full flex-col">
        {/* Logo */}
        <div className="flex h-24 items-center border-b border-transparent px-7 bg-gradient-to-br from-[#101c2c] via-[#1a2a3a] to-[#1a1a1a]">
          <div className="flex items-center gap-4">
            <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-gradient-to-br from-[#1a2a3a] to-[#69e07c] shadow-lg p-1.5">
              {/* Inline SVG logo */}
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 375 375" width="38" height="38" fill="none">
                <g>
                  <path fill="#1a1a1a" d="M 30.0625 -45.75 C 27.84375 -45.75 25.878906 -45.316406 24.171875 -44.453125 C 22.472656 -43.597656 21.046875 -42.359375 19.890625 -40.734375 C 18.734375 -39.117188 17.851562 -37.164062 17.25 -34.875 C 16.65625 -32.582031 16.359375 -30.007812 16.359375 -27.15625 C 16.359375 -23.289062 16.835938 -19.992188 17.796875 -17.265625 C 18.753906 -14.546875 20.238281 -12.46875 22.25 -11.03125 C 24.269531 -9.601562 26.875 -8.890625 30.0625 -8.890625 C 32.28125 -8.890625 34.503906 -9.132812 36.734375 -9.625 C 38.960938 -10.125 41.382812 -10.835938 44 -11.765625 L 44 -2.046875 C 41.582031 -1.054688 39.203125 -0.34375 36.859375 0.09375 C 34.515625 0.53125 31.890625 0.75 28.984375 0.75 C 23.359375 0.75 18.734375 -0.410156 15.109375 -2.734375 C 11.484375 -5.066406 8.796875 -8.332031 7.046875 -12.53125 C 5.304688 -16.726562 4.4375 -21.625 4.4375 -27.21875 C 4.4375 -31.351562 5 -35.140625 6.125 -38.578125 C 7.25 -42.015625 8.890625 -44.988281 11.046875 -47.5 C 13.210938 -50.019531 15.890625 -51.960938 19.078125 -53.328125 C 22.265625 -54.703125 25.925781 -55.390625 30.0625 -55.390625 C 32.78125 -55.390625 35.5 -55.046875 38.21875 -54.359375 C 40.945312 -53.671875 43.554688 -52.726562 46.046875 -51.53125 L 42.3125 -42.125 C 40.269531 -43.09375 38.210938 -43.9375 36.140625 -44.65625 C 34.078125 -45.382812 32.050781 -45.75 30.0625 -45.75 Z" />
                  <circle cx="155" cy="63" r="31" fill="#69e07c" />
                  <circle cx="135" cy="221" r="31" fill="#69e07c" />
                  <circle cx="240" cy="221" r="31" fill="#69e07c" />
                </g>
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-extrabold tracking-tight text-white drop-shadow-sm">CITYLENS</h1>
              <p className="text-xs text-[#69e07c] font-semibold mt-1">Smart City Platform</p>
            </div>
          </div>
        </div>
        {/* Navigation */}
        <nav className="flex-1 space-y-1 overflow-y-auto p-4 custom-scrollbar">
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            const Icon = item.icon;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={cn(
                  'group relative flex items-center gap-4 rounded-xl px-5 py-3 text-base font-semibold transition-all',
                  isActive
                    ? 'bg-gradient-to-r from-[#69e07c]/90 to-[#101c2c]/80 text-white shadow-lg scale-[1.03]'
                    : 'text-gray-300 hover:bg-white/10 hover:text-white'
                )}
              >
                <Icon className={cn('h-6 w-6 flex-shrink-0 transition-transform group-hover:scale-110', isActive ? 'text-white' : 'text-[#69e07c] group-hover:text-white')} />
                <span>{item.name}</span>
                {isActive && (
                  <span className="absolute right-4 h-2 w-2 rounded-full bg-[#69e07c] shadow-lg" />
                )}
              </Link>
            );
          })}
        </nav>
        {/* Footer */}
        <div className="mt-auto border-t border-white/10 p-5 bg-gradient-to-br from-[#101c2c]/80 to-[#1a1a1a]/90">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-full bg-gradient-to-br from-[#69e07c] to-[#1a2a3a] shadow-md">
              <Circle className="h-5 w-5 text-white" />
            </div>
            <div className="flex-1 overflow-hidden">
              <p className="truncate text-base font-semibold text-white">Admin User</p>
              <p className="truncate text-xs text-[#69e07c]">admin@citylens.vn</p>
              <span className="inline-flex items-center gap-1 text-xs text-green-400 mt-1">
                <Circle className="h-2 w-2 fill-green-400 text-green-400" /> Online
              </span>
            </div>
            <button className="ml-2 flex h-9 w-9 items-center justify-center rounded-lg bg-white/10 hover:bg-[#69e07c]/90 transition-all" title="Đăng xuất">
              <LogOut className="h-5 w-5 text-white" />
            </button>
          </div>
        </div>
      </div>
    </aside>
  );
}
