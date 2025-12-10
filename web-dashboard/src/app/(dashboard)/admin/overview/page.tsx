// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

'use client';

import { useState, useEffect } from 'react';
import { 
  Users, 
  Activity, 
  AlertTriangle, 
  TrendingUp,
  Cloud,
  Wind,
  Car,
  Database,
  RefreshCw,
  Download,
  MapPin,
  Bell,
  Lightbulb,
  Siren
} from 'lucide-react';
import { adminService, type DashboardOverview, type RealTimeMetrics, type Alert } from '@/lib/admin-service';
import { cn } from '@/lib/utils';
import toast from 'react-hot-toast';

// ============================================
// KPI Card Component
// ============================================
function KPICard({ 
  title, 
  value,
  subtitle,
  icon: Icon,
  trend,
  color = 'blue',
  loading = false
}: { 
  title: string;
  value: string | number;
  subtitle?: string;
  icon: React.ElementType;
  trend?: { value: number; label: string };
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple';
  loading?: boolean;
}) {
  const colorClasses = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
    red: 'bg-red-500',
    purple: 'bg-purple-500'
  };

  return (
    <div className="bg-card rounded-xl shadow-sm border border-border p-6 hover:shadow-md transition-all">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-muted-foreground mb-2">{title}</p>
          {loading ? (
            <div className="h-8 w-24 bg-muted rounded animate-pulse"></div>
          ) : (
            <>
              <h3 className="text-3xl font-bold text-foreground mb-1">{value}</h3>
              {subtitle && (
                <p className="text-xs text-muted-foreground">{subtitle}</p>
              )}
              {trend && (
                <div className={cn(
                  "text-xs mt-2 flex items-center gap-1",
                  trend.value > 0 ? "text-green-600" : "text-red-600"
                )}>
                  <TrendingUp className={cn("w-3 h-3", trend.value < 0 && "rotate-180")} />
                  <span>{Math.abs(trend.value)}% {trend.label}</span>
                </div>
              )}
            </>
          )}
        </div>
        <div className={cn("p-3 rounded-lg", colorClasses[color])}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </div>
  );
}

// ============================================
// Alert Item Component
// ============================================
function AlertItem({ alert, onAcknowledge }: { alert: Alert; onAcknowledge: (id: string) => void }) {
  const severityColors = {
    info: 'bg-blue-100 text-blue-800 border-blue-200',
    warning: 'bg-yellow-100 text-yellow-800 border-yellow-200',
    critical: 'bg-red-100 text-red-800 border-red-200'
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'info': return <Lightbulb className="h-5 w-5 text-blue-600" />;
      case 'warning': return <AlertTriangle className="h-5 w-5 text-yellow-600" />;
      case 'critical': return <Siren className="h-5 w-5 text-red-600" />;
      default: return <Bell className="h-5 w-5" />;
    }
  };

  return (
    <div className={cn(
      "p-4 rounded-lg border",
      severityColors[alert.severity]
    )}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            {getSeverityIcon(alert.severity)}
            <h4 className="font-semibold text-sm">{alert.title}</h4>
          </div>
          <p className="text-xs opacity-90 mb-2">{alert.description}</p>
          <div className="flex items-center gap-3 text-xs">
            {alert.location && (
              <span className="flex items-center gap-1">
                <MapPin className="w-3 h-3" />
                {alert.location}
              </span>
            )}
            <span>{new Date(alert.timestamp).toLocaleString('vi-VN')}</span>
          </div>
        </div>
        <button
          onClick={() => onAcknowledge(alert.id)}
          className="px-3 py-1 text-xs rounded-md bg-white hover:bg-gray-50 border transition-colors"
        >
          Xử lý
        </button>
      </div>
    </div>
  );
}

// ============================================
// Main Admin Overview Page
// ============================================
export default function AdminOverviewPage() {
  const [overview, setOverview] = useState<DashboardOverview | null>(null);
  const [realTimeMetrics, setRealTimeMetrics] = useState<RealTimeMetrics | null>(null);
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchData = async (showToast = false) => {
    try {
      if (showToast) setRefreshing(true);
      
      const [overviewData, metricsData, alertsData] = await Promise.all([
        adminService.getDashboardOverview(),
        adminService.getRealTimeMetrics(),
        adminService.getActiveAlerts(undefined, 10)
      ]);

      setOverview(overviewData);
      setRealTimeMetrics(metricsData);
      setAlerts(alertsData);
      
      if (showToast) {
        toast.success('Dữ liệu đã được cập nhật!', { duration: 2000 });
      }
    } catch (error: any) {
      console.error('Failed to fetch admin data:', error);
      toast.error(error.response?.data?.detail || 'Không thể tải dữ liệu admin');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
    
    // Auto-refresh every 30 seconds
    const interval = setInterval(() => fetchData(), 30000);
    return () => clearInterval(interval);
  }, []);

  const handleAcknowledgeAlert = async (alertId: string) => {
    try {
      await adminService.acknowledgeAlert(alertId);
      toast.success('Đã xác nhận cảnh báo');
      setAlerts(prev => prev.filter(a => a.id !== alertId));
    } catch (error) {
      toast.error('Không thể xử lý cảnh báo');
    }
  };

  const handleExportData = async () => {
    try {
      toast.loading('Đang xuất dữ liệu...', { id: 'export' });
      await adminService.exportDataCSV('traffic', 7);
      toast.success('Xuất dữ liệu thành công!', { id: 'export' });
    } catch (error) {
      toast.error('Không thể xuất dữ liệu', { id: 'export' });
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-foreground">Admin Dashboard</h1>
          <p className="text-muted-foreground mt-1">
            Giám sát và quản lý hệ thống thành phố thông minh
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={handleExportData}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
          >
            <Download className="w-4 h-4" />
            Xuất dữ liệu
          </button>
          <button
            onClick={() => fetchData(true)}
            disabled={refreshing}
            className="px-4 py-2 bg-card border border-border rounded-lg hover:bg-muted transition-colors flex items-center gap-2"
          >
            <RefreshCw className={cn("w-4 h-4", refreshing && "animate-spin")} />
            Làm mới
          </button>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          title="Tổng người dùng"
          value={overview?.user_statistics.total || 0}
          subtitle={`${overview?.user_statistics.active || 0} đang hoạt động`}
          icon={Users}
          color="blue"
          loading={loading}
        />
        <KPICard
          title="Cảnh báo quan trọng"
          value={overview?.alert_statistics.critical || 0}
          subtitle={`${alerts.filter(a => a.severity === 'critical').length} đang chờ xử lý`}
          icon={AlertTriangle}
          color="red"
          loading={loading}
        />
        <KPICard
          title="Dữ liệu giao thông (24h)"
          value={overview?.entity_statistics.traffic.last_24h || 0}
          subtitle={`${overview?.entity_statistics.traffic.total || 0} tổng`}
          icon={Car}
          color="green"
          loading={loading}
        />
        <KPICard
          title="Trạng thái hệ thống"
          value={overview?.system_health.status === 'healthy' ? 'Tốt' : 'Lỗi'}
          subtitle={`DB: ${overview?.system_health.database || 'N/A'}`}
          icon={Database}
          color={overview?.system_health.status === 'healthy' ? 'green' : 'red'}
          loading={loading}
        />
      </div>

      {/* Real-time Metrics */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Weather */}
        <div className="bg-card rounded-xl shadow-sm border border-border p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-blue-100 rounded-lg">
              <Cloud className="w-5 h-5 text-blue-600" />
            </div>
            <h3 className="font-semibold text-foreground">Thời tiết</h3>
          </div>
          {loading ? (
            <div className="space-y-2">
              <div className="h-4 bg-muted rounded animate-pulse"></div>
              <div className="h-4 bg-muted rounded animate-pulse w-3/4"></div>
            </div>
          ) : (
            <div className="space-y-2">
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold text-foreground">
                  {realTimeMetrics?.weather.latest.temperature?.toFixed(1) || '--'}°C
                </span>
                <span className="text-sm text-muted-foreground">
                  {realTimeMetrics?.weather.latest.humidity || '--'}% độ ẩm
                </span>
              </div>
              <p className="text-sm text-muted-foreground">
                {realTimeMetrics?.weather.latest.description || 'Không có dữ liệu'}
              </p>
              {realTimeMetrics?.weather.latest.observed_at && (
                <p className="text-xs text-muted-foreground">
                  Cập nhật: {new Date(realTimeMetrics.weather.latest.observed_at).toLocaleTimeString('vi-VN')}
                </p>
              )}
            </div>
          )}
        </div>

        {/* Air Quality */}
        <div className="bg-card rounded-xl shadow-sm border border-border p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-green-100 rounded-lg">
              <Wind className="w-5 h-5 text-green-600" />
            </div>
            <h3 className="font-semibold text-foreground">Chất lượng không khí</h3>
          </div>
          {loading ? (
            <div className="space-y-2">
              <div className="h-4 bg-muted rounded animate-pulse"></div>
              <div className="h-4 bg-muted rounded animate-pulse w-3/4"></div>
            </div>
          ) : (
            <div className="space-y-2">
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold text-foreground">
                  AQI {realTimeMetrics?.air_quality.latest.aqi || '--'}
                </span>
              </div>
              <div className="flex gap-3 text-sm text-muted-foreground">
                <span>PM2.5: {realTimeMetrics?.air_quality.latest.pm25 || '--'}</span>
                <span>PM10: {realTimeMetrics?.air_quality.latest.pm10 || '--'}</span>
              </div>
              {realTimeMetrics?.air_quality.latest.observed_at && (
                <p className="text-xs text-muted-foreground">
                  Cập nhật: {new Date(realTimeMetrics.air_quality.latest.observed_at).toLocaleTimeString('vi-VN')}
                </p>
              )}
            </div>
          )}
        </div>

        {/* Traffic */}
        <div className="bg-card rounded-xl shadow-sm border border-border p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-purple-100 rounded-lg">
              <Car className="w-5 h-5 text-purple-600" />
            </div>
            <h3 className="font-semibold text-foreground">Giao thông</h3>
          </div>
          {loading ? (
            <div className="space-y-2">
              <div className="h-4 bg-muted rounded animate-pulse"></div>
              <div className="h-4 bg-muted rounded animate-pulse w-3/4"></div>
            </div>
          ) : (
            <div className="space-y-2">
              <div className="flex items-baseline gap-2">
                <span className="text-3xl font-bold text-foreground">
                  {realTimeMetrics?.traffic.latest.intensity ? 
                    `${(realTimeMetrics.traffic.latest.intensity * 100).toFixed(0)}%` : '--'}
                </span>
                <span className="text-sm text-muted-foreground">mật độ</span>
              </div>
              <p className="text-sm text-muted-foreground">
                Tốc độ TB: {realTimeMetrics?.traffic.latest.average_speed || '--'} km/h
              </p>
              {realTimeMetrics?.traffic.latest.observed_at && (
                <p className="text-xs text-muted-foreground">
                  Cập nhật: {new Date(realTimeMetrics.traffic.latest.observed_at).toLocaleTimeString('vi-VN')}
                </p>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Active Alerts */}
      <div className="bg-card rounded-xl shadow-sm border border-border p-6">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-red-100 rounded-lg">
              <Bell className="w-5 h-5 text-red-600" />
            </div>
            <h3 className="text-lg font-semibold text-foreground">Cảnh báo đang hoạt động</h3>
          </div>
          <span className="text-sm text-muted-foreground">
            {alerts.length} cảnh báo
          </span>
        </div>
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {loading ? (
            Array.from({ length: 3 }).map((_, i) => (
              <div key={i} className="h-24 bg-muted rounded animate-pulse"></div>
            ))
          ) : alerts.length > 0 ? (
            alerts.map(alert => (
              <AlertItem 
                key={alert.id} 
                alert={alert} 
                onAcknowledge={handleAcknowledgeAlert}
              />
            ))
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <Bell className="w-12 h-12 mx-auto mb-3 opacity-50" />
              <p>Không có cảnh báo nào đang hoạt động</p>
            </div>
          )}
        </div>
      </div>

      {/* Quick Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Weather Stats */}
        <div className="bg-card rounded-xl shadow-sm border border-border p-6">
          <h3 className="font-semibold text-foreground mb-4">Thống kê thời tiết</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">7 ngày qua</span>
              <span className="font-medium">{overview?.entity_statistics.weather.last_7d || 0} quan sát</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">24 giờ qua</span>
              <span className="font-medium">{overview?.entity_statistics.weather.last_24h || 0} quan sát</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Tổng dữ liệu</span>
              <span className="font-medium">{overview?.entity_statistics.weather.total || 0}</span>
            </div>
          </div>
        </div>

        {/* Air Quality Stats */}
        <div className="bg-card rounded-xl shadow-sm border border-border p-6">
          <h3 className="font-semibold text-foreground mb-4">Thống kê không khí</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">7 ngày qua</span>
              <span className="font-medium">{overview?.entity_statistics.air_quality.last_7d || 0} quan sát</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">24 giờ qua</span>
              <span className="font-medium">{overview?.entity_statistics.air_quality.last_24h || 0} quan sát</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Tổng dữ liệu</span>
              <span className="font-medium">{overview?.entity_statistics.air_quality.total || 0}</span>
            </div>
          </div>
        </div>

        {/* Parking Stats */}
        <div className="bg-card rounded-xl shadow-sm border border-border p-6">
          <h3 className="font-semibold text-foreground mb-4">Bãi đỗ xe</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Tổng số chỗ</span>
              <span className="font-medium">{overview?.entity_statistics.parking.total || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Đang trống</span>
              <span className="font-medium text-green-600">{overview?.entity_statistics.parking.available || 0}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-sm text-muted-foreground">Đang sử dụng</span>
              <span className="font-medium text-red-600">{overview?.entity_statistics.parking.occupied || 0}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
