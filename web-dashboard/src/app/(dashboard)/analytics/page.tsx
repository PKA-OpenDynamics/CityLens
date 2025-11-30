// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

'use client';

import { useState } from 'react';
import { Download } from 'lucide-react';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts';
import { cn } from '@/lib/utils';
import { Select } from '@/components/ui/select';

// Demo data for charts
const reportTrendData = [
  { month: 'T6', reports: 45, resolved: 38 },
  { month: 'T7', reports: 52, resolved: 42 },
  { month: 'T8', reports: 61, resolved: 55 },
  { month: 'T9', reports: 78, resolved: 65 },
  { month: 'T10', reports: 89, resolved: 72 },
  { month: 'T11', reports: 95, resolved: 80 },
];

const districtData = [
  { name: 'Đống Đa', reports: 28 },
  { name: 'Ba Đình', reports: 22 },
  { name: 'Hoàn Kiếm', reports: 18 },
  { name: 'Cầu Giấy', reports: 15 },
  { name: 'Thanh Xuân', reports: 12 },
  { name: 'Hoàng Mai', reports: 10 },
  { name: 'Long Biên', reports: 8 },
  { name: 'Hai Bà Trưng', reports: 6 },
];

const incidentTypeData = [
  { name: 'Đường hỏng', value: 35 },
  { name: 'Kẹt xe', value: 28 },
  { name: 'Ngập nước', value: 18 },
  { name: 'Ô nhiễm', value: 12 },
  { name: 'Khác', value: 7 },
];

const dailyActivityData = [
  { hour: '00:00', reports: 2 },
  { hour: '03:00', reports: 1 },
  { hour: '06:00', reports: 5 },
  { hour: '09:00', reports: 15 },
  { hour: '12:00', reports: 12 },
  { hour: '15:00', reports: 18 },
  { hour: '18:00', reports: 25 },
  { hour: '21:00', reports: 8 },
];

const kpiData = [
  { label: 'Thời gian xử lý TB', value: '2.5 ngày', change: -12, trend: 'down' },
  { label: 'Tỷ lệ giải quyết', value: '84%', change: 5, trend: 'up' },
  { label: 'Mức độ hài lòng', value: '4.2/5', change: 8, trend: 'up' },
  { label: 'Báo cáo/ngày', value: '12.5', change: 15, trend: 'up' },
];

const timeRangeOptions = [
  { value: '7d', label: '7 ngày qua' },
  { value: '30d', label: '30 ngày qua' },
  { value: '90d', label: '90 ngày qua' },
  { value: '1y', label: '1 năm qua' },
];

// Color palette: chỉ dùng xanh lá và các biến thể xám/đen
const CHART_COLORS = {
  primary: 'hsl(142, 65%, 22%)', // Xanh lá đậm
  primaryLight: 'hsl(142, 65%, 35%)', // Xanh lá nhạt hơn
  secondary: 'hsl(0, 0%, 60%)', // Xám trung bình
  secondaryLight: 'hsl(0, 0%, 75%)', // Xám nhạt
  grid: 'hsl(0, 0%, 92%)', // Grid line
  gridDark: 'hsl(0, 0%, 20%)', // Grid line dark mode
  text: 'hsl(0, 0%, 45%)', // Text muted
  textDark: 'hsl(0, 0%, 65%)', // Text muted dark mode
};

// Generate shades for pie chart - chỉ dùng xanh lá và xám
const getPieColor = (index: number, total: number) => {
  if (index === 0) return CHART_COLORS.primary;
  const grayShade = 60 + (index * 5);
  return `hsl(0, 0%, ${Math.min(grayShade, 85)}%)`;
};

export default function AnalyticsPage() {
  const [timeRange, setTimeRange] = useState('30d');

  return (
    <div className="animate-fade-in space-y-6">
      {/* Header - Simplified */}
      <div className="flex items-start justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">
            Phân tích dữ liệu
          </h1>
          <p className="mt-2 text-muted-foreground">
            Thống kê và phân tích chuyên sâu về các chỉ số thành phố
          </p>
        </div>
        <div className="flex items-center gap-3">
          <Select
            options={timeRangeOptions}
            value={timeRange}
            onChange={setTimeRange}
            className="w-40"
          />
          <button className="flex items-center gap-2 rounded-lg border border-border bg-background px-4 py-2 text-sm font-medium hover:bg-muted transition-all">
            <Download className="h-4 w-4" />
            Xuất báo cáo
          </button>
        </div>
      </div>

      {/* KPI Cards - Clean design */}
      <div className="grid grid-cols-4 gap-4">
        {kpiData.map((kpi, index) => (
          <div key={index} className="rounded-xl border border-border bg-card p-6 hover:shadow-md transition-shadow">
            <p className="text-sm font-medium text-muted-foreground mb-3">{kpi.label}</p>
            <p className="text-3xl font-bold text-foreground mb-3">{kpi.value}</p>
            <div className="flex items-center gap-2">
              <span
                className={cn(
                  'text-sm font-semibold',
                  kpi.trend === 'up' 
                    ? 'text-accent' 
                    : 'text-foreground/60'
                )}
              >
                {kpi.change > 0 ? '+' : ''}{kpi.change}%
              </span>
              <span className="text-xs text-muted-foreground">so với kỳ trước</span>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-2 gap-6">
        {/* Report Trend Chart */}
        <div className="rounded-xl border border-border bg-card p-6">
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-foreground mb-1">Xu hướng báo cáo</h3>
            <p className="text-sm text-muted-foreground">Số lượng báo cáo theo tháng</p>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={reportTrendData}>
              <defs>
                <linearGradient id="colorReports" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={CHART_COLORS.primary} stopOpacity={0.3}/>
                  <stop offset="95%" stopColor={CHART_COLORS.primary} stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorResolved" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={CHART_COLORS.secondary} stopOpacity={0.3}/>
                  <stop offset="95%" stopColor={CHART_COLORS.secondary} stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke={CHART_COLORS.grid}
                className="dark:stroke-[hsl(0,0%,20%)]"
              />
              <XAxis 
                dataKey="month" 
                stroke={CHART_COLORS.text}
                className="dark:stroke-[hsl(0,0%,65%)]"
                fontSize={12} 
              />
              <YAxis 
                stroke={CHART_COLORS.text}
                className="dark:stroke-[hsl(0,0%,65%)]"
                fontSize={12} 
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '8px',
                  color: 'hsl(var(--foreground))',
                }}
              />
              <Legend 
                wrapperStyle={{ fontSize: '12px' }}
                iconType="circle"
              />
              <Area
                type="monotone"
                dataKey="reports"
                name="Tổng báo cáo"
                stroke={CHART_COLORS.primary}
                fillOpacity={1}
                fill="url(#colorReports)"
                strokeWidth={2}
              />
              <Area
                type="monotone"
                dataKey="resolved"
                name="Đã giải quyết"
                stroke={CHART_COLORS.secondary}
                fillOpacity={1}
                fill="url(#colorResolved)"
                strokeWidth={2}
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* District Distribution */}
        <div className="rounded-xl border border-border bg-card p-6">
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-foreground mb-1">Phân bố theo quận</h3>
            <p className="text-sm text-muted-foreground">Số lượng báo cáo theo quận/huyện</p>
          </div>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={districtData} layout="vertical">
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke={CHART_COLORS.grid}
                className="dark:stroke-[hsl(0,0%,20%)]"
              />
              <XAxis 
                type="number" 
                stroke={CHART_COLORS.text}
                className="dark:stroke-[hsl(0,0%,65%)]"
                fontSize={12} 
              />
              <YAxis 
                dataKey="name" 
                type="category" 
                stroke={CHART_COLORS.text}
                className="dark:stroke-[hsl(0,0%,65%)]"
                fontSize={12} 
                width={80} 
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '8px',
                  color: 'hsl(var(--foreground))',
                }}
              />
              <Bar 
                dataKey="reports" 
                name="Báo cáo" 
                radius={[0, 4, 4, 0]}
                fill={CHART_COLORS.primary}
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-3 gap-6">
        {/* Incident Type Pie Chart */}
        <div className="rounded-xl border border-border bg-card p-6">
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-foreground mb-1">Loại sự cố</h3>
            <p className="text-sm text-muted-foreground">Phân loại báo cáo theo loại</p>
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={incidentTypeData}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={2}
                dataKey="value"
              >
                {incidentTypeData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={getPieColor(index, incidentTypeData.length)} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '8px',
                  color: 'hsl(var(--foreground))',
                }}
              />
            </PieChart>
          </ResponsiveContainer>
          <div className="grid grid-cols-2 gap-3 mt-6">
            {incidentTypeData.map((item, index) => (
              <div key={index} className="flex items-center gap-2">
                <div
                  className="w-3 h-3 rounded-full flex-shrink-0"
                  style={{ backgroundColor: getPieColor(index, incidentTypeData.length) }}
                />
                <span className="text-xs text-muted-foreground flex-1 truncate">{item.name}</span>
                <span className="text-xs font-semibold text-foreground">{item.value}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Daily Activity */}
        <div className="col-span-2 rounded-xl border border-border bg-card p-6">
          <div className="mb-6">
            <h3 className="text-lg font-semibold text-foreground mb-1">Hoạt động trong ngày</h3>
            <p className="text-sm text-muted-foreground">Phân bố báo cáo theo giờ</p>
          </div>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={dailyActivityData}>
              <CartesianGrid 
                strokeDasharray="3 3" 
                stroke={CHART_COLORS.grid}
                className="dark:stroke-[hsl(0,0%,20%)]"
              />
              <XAxis 
                dataKey="hour" 
                stroke={CHART_COLORS.text}
                className="dark:stroke-[hsl(0,0%,65%)]"
                fontSize={12} 
              />
              <YAxis 
                stroke={CHART_COLORS.text}
                className="dark:stroke-[hsl(0,0%,65%)]"
                fontSize={12} 
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: 'hsl(var(--card))',
                  border: '1px solid hsl(var(--border))',
                  borderRadius: '8px',
                  color: 'hsl(var(--foreground))',
                }}
              />
              <Line
                type="monotone"
                dataKey="reports"
                name="Báo cáo"
                stroke={CHART_COLORS.primary}
                strokeWidth={2.5}
                dot={{ fill: CHART_COLORS.primary, strokeWidth: 2, r: 4 }}
                activeDot={{ r: 6, fill: CHART_COLORS.primary }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Summary Stats - Clean design */}
      <div className="rounded-xl border border-border bg-card p-6">
        <h3 className="text-lg font-semibold text-foreground mb-6">Tổng quan hiệu suất</h3>
        <div className="grid grid-cols-5 gap-4">
          <div className="text-center p-5 rounded-lg border border-border bg-muted/30">
            <p className="text-3xl font-bold text-foreground mb-2">420</p>
            <p className="text-sm text-muted-foreground">Tổng báo cáo</p>
          </div>
          <div className="text-center p-5 rounded-lg border border-border bg-muted/30">
            <p className="text-3xl font-bold text-accent mb-2">352</p>
            <p className="text-sm text-muted-foreground">Đã giải quyết</p>
          </div>
          <div className="text-center p-5 rounded-lg border border-border bg-muted/30">
            <p className="text-3xl font-bold text-foreground/70 mb-2">45</p>
            <p className="text-sm text-muted-foreground">Đang xử lý</p>
          </div>
          <div className="text-center p-5 rounded-lg border border-border bg-muted/30">
            <p className="text-3xl font-bold text-foreground/60 mb-2">23</p>
            <p className="text-sm text-muted-foreground">Chờ xác nhận</p>
          </div>
          <div className="text-center p-5 rounded-lg border border-border bg-muted/30">
            <p className="text-3xl font-bold text-foreground mb-2">1,234</p>
            <p className="text-sm text-muted-foreground">Người đóng góp</p>
          </div>
        </div>
      </div>
    </div>
  );
}
