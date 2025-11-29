// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

'use client';

import { Info, MapPin, Navigation, TrendingUp } from 'lucide-react';

interface MapStatsProps {
  totalMarkers?: number;
  activeAlerts?: number;
  coverage?: string;
}

export default function MapStats({ 
  totalMarkers = 2847, 
  activeAlerts = 12,
  coverage = '98.5%'
}: MapStatsProps) {
  return (
    <div className="absolute bottom-20 left-4 z-[1000] bg-white dark:bg-gray-800 rounded-lg shadow-lg p-4 min-w-[280px]">
      <h3 className="text-sm font-semibold text-gray-900 dark:text-white mb-3 flex items-center gap-2">
        <Info className="h-4 w-4 text-accent" />
        Thông tin bản đồ
      </h3>
      
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-gray-600 dark:text-gray-300">
            <MapPin className="h-4 w-4 text-accent" />
            <span className="text-sm">Tổng điểm đánh dấu</span>
          </div>
          <span className="text-sm font-semibold text-gray-900 dark:text-white">
            {totalMarkers.toLocaleString()}
          </span>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-gray-600 dark:text-gray-300">
            <Navigation className="h-4 w-4 text-red-500" />
            <span className="text-sm">Cảnh báo hoạt động</span>
          </div>
          <span className="text-sm font-semibold text-red-500">
            {activeAlerts}
          </span>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-gray-600 dark:text-gray-300">
            <TrendingUp className="h-4 w-4 text-green-500" />
            <span className="text-sm">Độ phủ dữ liệu</span>
          </div>
          <span className="text-sm font-semibold text-green-500">
            {coverage}
          </span>
        </div>
      </div>

      <div className="mt-4 pt-3 border-t border-gray-200 dark:border-gray-700">
        <div className="text-xs text-gray-500 dark:text-gray-400">
          Cập nhật lần cuối: {new Date().toLocaleTimeString('vi-VN')}
        </div>
      </div>
    </div>
  );
}
