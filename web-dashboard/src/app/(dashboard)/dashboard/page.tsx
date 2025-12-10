// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  FileText, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  MapPin,
  Wind,
  Droplets,
  Activity,
  Map,
  Building2,
  Route,
  Layers,
  RefreshCw
} from 'lucide-react';
import { 
  reportApi, 
  healthApi, 
  realtimeApi,
  geographicStatsApi,
  type ReportStatistics,
  type WeatherData,
  type AirQualityData,
  type TrafficHotspot,
  type GeographicStatistics
} from '@/lib/api';
import { cn } from '@/lib/utils';

// ============================================
// Overview Card Component
// ============================================
function OverviewCard({ 
  title, 
  children,
  className,
  loading = false,
  headerAction
}: { 
  title: string;
  children: React.ReactNode;
  className?: string;
  loading?: boolean;
  headerAction?: React.ReactNode;
}) {
  return (
    <div className={cn(
      "bg-card rounded-xl shadow-sm border border-border p-6",
      "hover:shadow-md transition-shadow",
      className
    )}>
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-semibold text-foreground">{title}</h2>
        {headerAction}
      </div>
      {loading ? (
        <div className="animate-pulse space-y-3">
          <div className="h-4 bg-muted rounded w-3/4"></div>
          <div className="h-4 bg-muted rounded w-1/2"></div>
          <div className="h-4 bg-muted rounded w-2/3"></div>
        </div>
      ) : (
        children
      )}
    </div>
  );
}

// ============================================
// Stat Item Component
// ============================================
function StatItem({ 
  label, 
  value, 
  unit,
  color = 'default',
  icon: Icon
}: { 
  label: string;
  value: string | number;
  unit?: string;
  color?: 'default' | 'green' | 'yellow' | 'red' | 'blue' | 'purple';
  icon?: React.ElementType;
}) {
  const colorClasses = {
    default: 'text-foreground',
    green: 'text-green-600 dark:text-green-400',
    yellow: 'text-yellow-600 dark:text-yellow-400',
    red: 'text-red-600 dark:text-red-400',
    blue: 'text-blue-600 dark:text-blue-400',
    purple: 'text-purple-600 dark:text-purple-400'
  };

  return (
    <div className="flex items-center justify-between py-2 border-b border-border/50 last:border-0">
      <div className="flex items-center gap-2">
        {Icon && <Icon className="w-4 h-4 text-muted-foreground" />}
        <span className="text-sm text-muted-foreground">{label}</span>
      </div>
      <span className={cn("text-sm font-semibold", colorClasses[color])}>
        {value}{unit && <span className="text-xs ml-1 text-muted-foreground">{unit}</span>}
      </span>
    </div>
  );
}

// ============================================
// AQI Color Helper
// ============================================
function getAQIColor(aqi: number): 'green' | 'yellow' | 'red' {
  if (aqi <= 50) return 'green';
  if (aqi <= 100) return 'yellow';
  return 'red';
}

function getAQILabel(aqi: number): string {
  if (aqi <= 50) return 'Tốt';
  if (aqi <= 100) return 'Trung bình';
  if (aqi <= 150) return 'Không tốt cho nhóm nhạy cảm';
  if (aqi <= 200) return 'Không tốt';
  if (aqi <= 300) return 'Rất không tốt';
  return 'Nguy hiểm';
}

// ============================================
// Traffic Congestion Color Helper
// ============================================
function getCongestionColor(level: string): 'green' | 'yellow' | 'red' {
  if (level === 'free_flow' || level === 'light') return 'green';
  if (level === 'moderate') return 'yellow';
  return 'red';
}

function getCongestionLabel(level: string): string {
  const labels: Record<string, string> = {
    'free_flow': 'Thông thoáng',
    'light': 'Nhẹ',
    'moderate': 'Đông đúc',
    'heavy': 'Ùn tắc',
    'severe': 'Tắc nghẽn'
  };
  return labels[level] || level;
}

// ============================================
// Main Dashboard Component
// ============================================
export default function DashboardPage() {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [apiStatus, setApiStatus] = useState<'online' | 'offline' | 'checking'>('checking');
  
  const [statistics, setStatistics] = useState<ReportStatistics | null>(null);
  const [appReports, setAppReports] = useState<{ total: number; pending: number; processing: number; resolved: number }>({ total: 0, pending: 0, processing: 0, resolved: 0 });
  const [weather, setWeather] = useState<WeatherData | null>(null);
  const [airQuality, setAirQuality] = useState<AirQualityData | null>(null);
  const [trafficHotspots, setTrafficHotspots] = useState<TrafficHotspot[]>([]);
  const [geoStats, setGeoStats] = useState<GeographicStatistics | null>(null);

  const fetchData = async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    else setLoading(true);
    
    try {
      await healthApi.check();
      setApiStatus('online');
    } catch {
      setApiStatus('offline');
    }

    // Fetch MongoDB Atlas reports stats
    try {
      const appReportsResponse = await fetch('http://localhost:8000/api/v1/app/reports?limit=1000');
      if (appReportsResponse.ok) {
        const appReportsData = await appReportsResponse.json();
        const reports = appReportsData.reports || [];
        setAppReports({
          total: reports.length,
          pending: reports.filter((r: any) => r.status === 'pending').length,
          processing: reports.filter((r: any) => r.status === 'processing').length,
          resolved: reports.filter((r: any) => r.status === 'resolved').length,
        });
      }
    } catch (error) {
      console.error('Failed to fetch app reports:', error);
    }

    const [statsResult, weatherResult, aqiResult, trafficResult, geoResult] = await Promise.allSettled([
      reportApi.getStatistics(),
      realtimeApi.getWeather(),
      realtimeApi.getAirQuality(),
      realtimeApi.getTrafficHotspots(),
      geographicStatsApi.getStatistics()
    ]);

    if (statsResult.status === 'fulfilled') setStatistics(statsResult.value);
    if (weatherResult.status === 'fulfilled') setWeather(weatherResult.value);
    if (aqiResult.status === 'fulfilled') setAirQuality(aqiResult.value);
    if (trafficResult.status === 'fulfilled') setTrafficHotspots(trafficResult.value.hotspots || []);
    if (geoResult.status === 'fulfilled') setGeoStats(geoResult.value);

    setLoading(false);
    setRefreshing(false);
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(() => fetchData(true), 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Tổng quan Hà Nội</h1>
          <p className="text-muted-foreground mt-1">Theo dõi tình hình đô thị thời gian thực</p>
        </div>
        <div className="flex items-center gap-3">
          <div className={cn(
            "flex items-center px-3 py-1.5 rounded-full text-sm font-medium",
            apiStatus === 'online' 
              ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' 
              : apiStatus === 'offline' 
                ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                : 'bg-muted text-muted-foreground'
          )}>
            <span className={cn(
              "w-2 h-2 rounded-full mr-2",
              apiStatus === 'online' ? 'bg-green-500' : apiStatus === 'offline' ? 'bg-red-500' : 'bg-muted-foreground animate-pulse'
            )}></span>
            {apiStatus === 'online' ? 'Đang hoạt động' : apiStatus === 'offline' ? 'Mất kết nối' : 'Đang kiểm tra...'}
          </div>
          
          <button
            onClick={() => fetchData(true)}
            disabled={refreshing}
            className={cn(
              "flex items-center gap-2 px-4 py-2 rounded-lg",
              "bg-green-600 text-white hover:bg-green-700 transition-colors",
              "disabled:opacity-50 disabled:cursor-not-allowed"
            )}
          >
            <RefreshCw className={cn("w-4 h-4", refreshing && "animate-spin")} />
            <span className="hidden sm:inline">Làm mới</span>
          </button>
        </div>
      </div>

      {/* Report Statistics Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-card rounded-xl border border-border p-4 hover:shadow-md transition-shadow">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-blue-50 dark:bg-blue-900/30">
              <FileText className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Tổng báo cáo</p>
              <p className="text-xl font-bold text-foreground">{loading ? '...' : (statistics?.total || 0) + appReports.total}</p>
              <p className="text-[10px] text-muted-foreground">Web: {statistics?.total || 0} • App: {appReports.total}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-card rounded-xl border border-border p-4 hover:shadow-md transition-shadow">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-yellow-50 dark:bg-yellow-900/30">
              <Clock className="w-5 h-5 text-yellow-600 dark:text-yellow-400" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Chờ xử lý</p>
              <p className="text-xl font-bold text-foreground">{loading ? '...' : (statistics?.pending || 0) + appReports.pending}</p>
              <p className="text-[10px] text-muted-foreground">Web: {statistics?.pending || 0} • App: {appReports.pending}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-card rounded-xl border border-border p-4 hover:shadow-md transition-shadow">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-green-50 dark:bg-green-900/30">
              <AlertTriangle className="w-5 h-5 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Đang xử lý</p>
              <p className="text-xl font-bold text-foreground">{loading ? '...' : (statistics?.in_progress || 0) + appReports.processing}</p>
              <p className="text-[10px] text-muted-foreground">Web: {statistics?.in_progress || 0} • App: {appReports.processing}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-card rounded-xl border border-border p-4 hover:shadow-md transition-shadow">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-green-50 dark:bg-green-900/30">
              <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <p className="text-xs text-muted-foreground">Đã giải quyết</p>
              <p className="text-xl font-bold text-foreground">{loading ? '...' : (statistics?.resolved || 0) + appReports.resolved}</p>
              <p className="text-[10px] text-muted-foreground">Web: {statistics?.resolved || 0} • App: {appReports.resolved}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        
        {/* Weather Card */}
        <OverviewCard title="Thời tiết Hà Nội" loading={loading}>
          {weather ? (
            <div className="space-y-1">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-4xl font-bold text-foreground">{Math.round(weather.weather.temperature)}°C</p>
                  <p className="text-sm text-muted-foreground capitalize">{weather.weather.description}</p>
                </div>
                <div className="text-right">
                  <p className="text-sm text-muted-foreground">Cảm giác như</p>
                  <p className="text-lg font-semibold text-foreground">
                    {weather.weather.feels_like ? Math.round(weather.weather.feels_like) : Math.round(weather.weather.temperature)}°C
                  </p>
                </div>
              </div>
              <StatItem label="Độ ẩm" value={weather.weather.humidity} unit="%" icon={Droplets} color="blue" />
              <StatItem label="Tốc độ gió" value={weather.weather.wind_speed.toFixed(1)} unit="m/s" icon={Wind} />
              <StatItem label="Áp suất" value={weather.weather.pressure} unit="hPa" />
              <StatItem label="Tầm nhìn" value={weather.weather.visibility ? (weather.weather.visibility / 1000).toFixed(1) : 'N/A'} unit="km" />
              <p className="text-xs text-muted-foreground mt-3 pt-2 border-t border-border/50">
                Nguồn: {weather.source} • Cập nhật: {new Date(weather.timestamp).toLocaleTimeString('vi-VN')}
              </p>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Không có dữ liệu thời tiết</p>
          )}
        </OverviewCard>

        {/* Air Quality Card */}
        <OverviewCard title="Chất lượng không khí" loading={loading}>
          {airQuality ? (
            <div className="space-y-1">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className={cn(
                    "text-4xl font-bold",
                    getAQIColor(airQuality.aqi.value) === 'green' ? 'text-green-600 dark:text-green-400' :
                    getAQIColor(airQuality.aqi.value) === 'yellow' ? 'text-yellow-600 dark:text-yellow-400' :
                    'text-red-600 dark:text-red-400'
                  )}>
                    {airQuality.aqi.value}
                  </p>
                  <p className="text-sm text-muted-foreground">AQI - {airQuality.aqi.level}</p>
                </div>
                <div className={cn(
                  "px-3 py-1 rounded-full text-sm font-medium",
                  getAQIColor(airQuality.aqi.value) === 'green' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' :
                  getAQIColor(airQuality.aqi.value) === 'yellow' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400' :
                  'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                )}>
                  {getAQILabel(airQuality.aqi.value)}
                </div>
              </div>
              <StatItem label="PM2.5" value={airQuality.pollutants.pm25.value ?? 'N/A'} unit="µg/m³" color={getAQIColor((airQuality.pollutants.pm25.value ?? 0) * 2)} />
              <StatItem label="PM10" value={airQuality.pollutants.pm10.value ?? 'N/A'} unit="µg/m³" />
              <StatItem label="O₃ (Ozone)" value={airQuality.pollutants.o3.value ?? 'N/A'} unit="µg/m³" />
              <StatItem label="NO₂" value={airQuality.pollutants.no2.value ?? 'N/A'} unit="µg/m³" />
              <p className="text-xs text-muted-foreground mt-3 pt-2 border-t border-border/50">
                Trạm: {airQuality.location.station}
              </p>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Không có dữ liệu chất lượng không khí</p>
          )}
        </OverviewCard>

        {/* Traffic Card */}
        <OverviewCard 
          title="Giao thông" 
          loading={loading}
          headerAction={
            <Link href="/geographic" className="text-sm text-accent hover:text-accent/80">
              Xem bản đồ
            </Link>
          }
        >
          {trafficHotspots.length > 0 ? (
            <div className="space-y-2">
              <p className="text-sm text-muted-foreground mb-3">
                {trafficHotspots.length} điểm nóng giao thông
              </p>
              {trafficHotspots.slice(0, 5).map((hotspot, index) => (
                <div key={`traffic-${index}`} className="flex items-center justify-between py-2 border-b border-border/50 last:border-0">
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <MapPin className="w-4 h-4 text-muted-foreground flex-shrink-0" />
                    <span className="text-sm text-foreground truncate">{hotspot.name}</span>
                  </div>
                  <span className={cn(
                    "text-xs px-2 py-1 rounded-full font-medium ml-2",
                    getCongestionColor(hotspot.traffic.congestion_level) === 'green' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' :
                    getCongestionColor(hotspot.traffic.congestion_level) === 'yellow' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400' :
                    'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                  )}>
                    {getCongestionLabel(hotspot.traffic.congestion_level)}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Không có dữ liệu giao thông</p>
          )}
        </OverviewCard>

        {/* Geographic Statistics Card */}
        <OverviewCard 
          title="Dữ liệu địa lý Hà Nội" 
          loading={loading}
          className="lg:col-span-2 xl:col-span-2"
          headerAction={
            <Link href="/geographic" className="text-sm text-accent hover:text-accent/80">
              Xem chi tiết
            </Link>
          }
        >
          {geoStats ? (
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-4 rounded-lg bg-muted/50">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <Layers className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                </div>
                <p className="text-2xl font-bold text-foreground">{(geoStats.administrative_boundaries?.total || 0).toLocaleString('vi-VN')}</p>
                <p className="text-xs text-muted-foreground">Ranh giới hành chính</p>
              </div>
              <div className="text-center p-4 rounded-lg bg-muted/50">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <Route className="w-5 h-5 text-green-600 dark:text-green-400" />
                </div>
                <p className="text-2xl font-bold text-foreground">{(geoStats.streets?.total || 0).toLocaleString('vi-VN')}</p>
                <p className="text-xs text-muted-foreground">Đường phố</p>
              </div>
              <div className="text-center p-4 rounded-lg bg-muted/50">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <Building2 className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                </div>
                <p className="text-2xl font-bold text-foreground">{(geoStats.buildings?.total || 0).toLocaleString('vi-VN')}</p>
                <p className="text-xs text-muted-foreground">Công trình</p>
              </div>
              <div className="text-center p-4 rounded-lg bg-muted/50">
                <div className="flex items-center justify-center gap-2 mb-2">
                  <Map className="w-5 h-5 text-orange-600 dark:text-orange-400" />
                </div>
                <p className="text-2xl font-bold text-foreground">{(geoStats.pois?.total || 0).toLocaleString('vi-VN')}</p>
                <p className="text-xs text-muted-foreground">Điểm quan tâm (POI)</p>
              </div>
            </div>
          ) : (
            <p className="text-sm text-muted-foreground">Không có dữ liệu địa lý</p>
          )}
          
          {geoStats && (
            <div className="mt-4 pt-4 border-t border-border/50">
              <p className="text-sm text-muted-foreground">
                Tổng cộng: <span className="font-semibold text-foreground">{(geoStats.summary?.total_features || 0).toLocaleString('vi-VN')}</span> đối tượng địa lý từ OpenStreetMap
              </p>
            </div>
          )}
        </OverviewCard>

        {/* Quick Links Card */}
        <OverviewCard title="Truy cập nhanh" className="xl:col-span-1">
          <div className="space-y-2">
            <Link 
              href="/geographic" 
              className="flex items-center gap-3 p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
            >
              <Map className="w-5 h-5 text-accent" />
              <div>
                <p className="text-sm font-medium text-foreground">Bản đồ địa lý</p>
                <p className="text-xs text-muted-foreground">Xem ranh giới, đường phố, công trình</p>
              </div>
            </Link>
            <Link 
              href="/reports" 
              className="flex items-center gap-3 p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
            >
              <FileText className="w-5 h-5 text-accent" />
              <div>
                <p className="text-sm font-medium text-foreground">Quản lý báo cáo</p>
                <p className="text-xs text-muted-foreground">Xem và xử lý báo cáo từ công dân</p>
              </div>
            </Link>
            <Link 
              href="/users" 
              className="flex items-center gap-3 p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors"
            >
              <Activity className="w-5 h-5 text-accent" />
              <div>
                <p className="text-sm font-medium text-foreground">Người dùng</p>
                <p className="text-xs text-muted-foreground">Quản lý tài khoản hệ thống</p>
              </div>
            </Link>
          </div>
        </OverviewCard>
      </div>
    </div>
  );
}
