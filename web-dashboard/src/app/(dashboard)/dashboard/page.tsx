'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { 
  FileText, 
  AlertTriangle, 
  CheckCircle, 
  Clock,
  Building,
  BarChart3,
  TrendingUp,
  TrendingDown,
  Eye,
  MapPin
} from 'lucide-react';
import { reportApi, facilityApi, healthApi, type ReportStatistics, type Report, type Facility } from '@/lib/api';

// Stat card component
function StatCard({ 
  title, 
  value, 
  icon: Icon, 
  trend,
  trendValue,
  color = 'blue',
  loading = false
}: { 
  title: string;
  value: string | number;
  icon: React.ElementType;
  trend?: 'up' | 'down';
  trendValue?: string;
  color?: 'blue' | 'green' | 'yellow' | 'red' | 'purple';
  loading?: boolean;
}) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400',
    green: 'bg-green-50 text-green-600 dark:bg-green-900/30 dark:text-green-400',
    yellow: 'bg-yellow-50 text-yellow-600 dark:bg-yellow-900/30 dark:text-yellow-400',
    red: 'bg-red-50 text-red-600 dark:bg-red-900/30 dark:text-red-400',
    purple: 'bg-purple-50 text-purple-600 dark:bg-purple-900/30 dark:text-purple-400'
  };

  if (loading) {
    return (
      <div className="bg-card rounded-xl shadow-sm border border-border p-6 animate-pulse">
        <div className="flex items-center justify-between">
          <div className="space-y-3">
            <div className="h-4 bg-muted rounded w-24"></div>
            <div className="h-8 bg-muted rounded w-16"></div>
          </div>
          <div className={`p-3 rounded-lg bg-muted`}>
            <div className="w-6 h-6 bg-muted-foreground/20 rounded"></div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-card rounded-xl shadow-sm border border-border p-6 hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-muted-foreground">{title}</p>
          <p className="text-2xl font-bold text-foreground mt-1">{value}</p>
          {trend && trendValue && (
            <div className="flex items-center mt-2">
              {trend === 'up' ? (
                <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
              ) : (
                <TrendingDown className="w-4 h-4 text-red-500 mr-1" />
              )}
              <span className={`text-sm ${trend === 'up' ? 'text-green-600' : 'text-red-600'}`}>
                {trendValue}
              </span>
            </div>
          )}
        </div>
        <div className={`p-3 rounded-lg ${colorClasses[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
      </div>
    </div>
  );
}

// Report item component
function ReportItem({ report }: { report: Report }) {
  const statusColors: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400',
    verified: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
    in_progress: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400',
    resolved: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400',
    rejected: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400'
  };

  const statusLabels: Record<string, string> = {
    pending: 'Chờ xử lý',
    verified: 'Đã xác nhận',
    in_progress: 'Đang xử lý',
    resolved: 'Đã giải quyết',
    rejected: 'Từ chối'
  };

  const categoryLabels: Record<string, string> = {
    infrastructure: 'Cơ sở hạ tầng',
    environment: 'Môi trường',
    traffic: 'Giao thông',
    security: 'An ninh',
    other: 'Khác'
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('vi-VN', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  return (
    <div className="flex items-start space-x-4 p-4 bg-muted/50 rounded-lg hover:bg-muted transition-colors">
      <div className="flex-shrink-0">
        <MapPin className="w-5 h-5 text-muted-foreground" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-foreground truncate">{report.title}</p>
        <p className="text-sm text-muted-foreground truncate">{report.description}</p>
        <div className="flex items-center mt-2 space-x-2">
          <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${statusColors[report.status] || statusColors.pending}`}>
            {statusLabels[report.status] || report.status}
          </span>
          <span className="text-xs text-muted-foreground">
            {categoryLabels[report.category] || report.category}
          </span>
        </div>
      </div>
      <div className="flex-shrink-0 text-xs text-muted-foreground">
        {formatDate(report.created_at)}
      </div>
    </div>
  );
}

// Facility item component
function FacilityItem({ facility }: { facility: Facility }) {
  const categoryLabels: Record<string, string> = {
    hospital: 'Bệnh viện',
    school: 'Trường học',
    park: 'Công viên',
    government: 'Cơ quan nhà nước',
    health: 'Y tế',
    education: 'Giáo dục',
    recreation: 'Giải trí',
    other: 'Khác'
  };

  return (
    <div className="flex items-center space-x-4 p-4 bg-muted/50 rounded-lg hover:bg-muted transition-colors">
      <div className="flex-shrink-0">
        <Building className="w-5 h-5 text-accent" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium text-foreground truncate">{facility.name}</p>
        <p className="text-xs text-muted-foreground">{categoryLabels[facility.category] || facility.category}</p>
      </div>
      {facility.rating && (
        <div className="flex items-center text-yellow-500">
          <span className="text-sm font-medium">{facility.rating.toFixed(1)}</span>
          <span className="ml-1">⭐</span>
        </div>
      )}
    </div>
  );
}

export default function DashboardPage() {
  const [statistics, setStatistics] = useState<ReportStatistics | null>(null);
  const [recentReports, setRecentReports] = useState<Report[]>([]);
  const [facilities, setFacilities] = useState<Facility[]>([]);
  const [loading, setLoading] = useState(true);
  const [apiStatus, setApiStatus] = useState<'online' | 'offline' | 'checking'>('checking');

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      
      // Check API health
      try {
        await healthApi.check();
        setApiStatus('online');
      } catch {
        setApiStatus('offline');
      }

      // Fetch statistics
      try {
        const stats = await reportApi.getStatistics();
        setStatistics(stats);
      } catch (error) {
        console.error('Failed to fetch statistics:', error);
        // Use fallback data
        setStatistics({
          total: 0,
          pending: 0,
          in_progress: 0,
          resolved: 0,
          verified: 0,
          today: 0,
          this_week: 0,
          resolution_rate: 0
        });
      }

      // Fetch recent reports
      try {
        const reportsResponse = await reportApi.getReports({ limit: 5 });
        setRecentReports(reportsResponse.reports || []);
      } catch (error) {
        console.error('Failed to fetch reports:', error);
        setRecentReports([]);
      }

      // Fetch facilities
      try {
        const facilitiesResponse = await facilityApi.getFacilities({ limit: 5 });
        setFacilities(facilitiesResponse.facilities || []);
      } catch (error) {
        console.error('Failed to fetch facilities:', error);
        setFacilities([]);
      }

      setLoading(false);
    };

    fetchData();
  }, []);

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground">Tổng quan</h1>
          <p className="text-muted-foreground mt-1">Theo dõi tình hình đô thị Hà Nội</p>
        </div>
        <div className="flex items-center space-x-4">
          <div className={`flex items-center px-3 py-1.5 rounded-full text-sm font-medium ${
            apiStatus === 'online' 
              ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' 
              : apiStatus === 'offline' 
                ? 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
                : 'bg-muted text-muted-foreground'
          }`}>
            <span className={`w-2 h-2 rounded-full mr-2 ${
              apiStatus === 'online' 
                ? 'bg-green-500' 
                : apiStatus === 'offline' 
                  ? 'bg-red-500'
                  : 'bg-muted-foreground animate-pulse'
            }`}></span>
            {apiStatus === 'online' ? 'API Online' : apiStatus === 'offline' ? 'API Offline' : 'Checking...'}
          </div>
          <Link
            href="/analytics"
            className="inline-flex items-center px-4 py-2 bg-accent text-white rounded-lg hover:bg-accent/90 transition-colors"
          >
            <BarChart3 className="w-5 h-5 mr-2" />
            Phân tích
          </Link>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Tổng báo cáo"
          value={statistics?.total || 0}
          icon={FileText}
          color="blue"
          loading={loading}
        />
        <StatCard
          title="Chờ xử lý"
          value={statistics?.pending || 0}
          icon={Clock}
          color="yellow"
          loading={loading}
        />
        <StatCard
          title="Đang xử lý"
          value={statistics?.in_progress || 0}
          icon={AlertTriangle}
          color="purple"
          loading={loading}
        />
        <StatCard
          title="Đã giải quyết"
          value={statistics?.resolved || 0}
          icon={CheckCircle}
          color="green"
          loading={loading}
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Reports */}
        <div className="bg-card rounded-xl shadow-sm border border-border p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-foreground">Báo cáo gần đây</h2>
            <Link 
              href="/reports" 
              className="text-sm text-accent hover:text-accent/80 flex items-center"
            >
              Xem tất cả
              <Eye className="w-4 h-4 ml-1" />
            </Link>
          </div>
          <div className="space-y-3">
            {loading ? (
              // Loading skeleton
              Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="animate-pulse p-4 bg-muted/50 rounded-lg">
                  <div className="flex items-start space-x-4">
                    <div className="w-5 h-5 bg-muted rounded"></div>
                    <div className="flex-1 space-y-2">
                      <div className="h-4 bg-muted rounded w-3/4"></div>
                      <div className="h-3 bg-muted rounded w-1/2"></div>
                    </div>
                  </div>
                </div>
              ))
            ) : recentReports.length > 0 ? (
              recentReports.map((report) => (
                <ReportItem key={report.id} report={report} />
              ))
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <AlertTriangle className="w-12 h-12 mx-auto text-muted mb-3" />
                <p>Chưa có báo cáo nào</p>
              </div>
            )}
          </div>
        </div>

        {/* Facilities */}
        <div className="bg-card rounded-xl shadow-sm border border-border p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-foreground">Cơ sở tiện ích</h2>
            <Link 
              href="/map" 
              className="text-sm text-accent hover:text-accent/80 flex items-center"
            >
              Xem bản đồ
              <MapPin className="w-4 h-4 ml-1" />
            </Link>
          </div>
          <div className="space-y-3">
            {loading ? (
              // Loading skeleton
              Array.from({ length: 3 }).map((_, i) => (
                <div key={i} className="animate-pulse p-4 bg-muted/50 rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className="w-5 h-5 bg-muted rounded"></div>
                    <div className="flex-1 space-y-2">
                      <div className="h-4 bg-muted rounded w-3/4"></div>
                      <div className="h-3 bg-muted rounded w-1/4"></div>
                    </div>
                  </div>
                </div>
              ))
            ) : facilities.length > 0 ? (
              facilities.map((facility) => (
                <FacilityItem key={facility.id} facility={facility} />
              ))
            ) : (
              <div className="text-center py-8 text-muted-foreground">
                <Building className="w-12 h-12 mx-auto text-muted mb-3" />
                <p>Chưa có dữ liệu cơ sở</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-gradient-to-r from-accent to-accent/80 rounded-xl p-6 text-white">
        <h2 className="text-lg font-semibold mb-2">Hành động nhanh</h2>
        <p className="text-white/80 mb-4">Quản lý và theo dõi tình hình đô thị</p>
        <div className="flex flex-wrap gap-3">
          <Link
            href="/reports/new"
            className="inline-flex items-center px-4 py-2 bg-white text-accent rounded-lg hover:bg-white/90 transition-colors font-medium"
          >
            <AlertTriangle className="w-5 h-5 mr-2" />
            Tạo báo cáo mới
          </Link>
          <Link
            href="/map"
            className="inline-flex items-center px-4 py-2 bg-white/20 text-white rounded-lg hover:bg-white/30 transition-colors font-medium"
          >
            <MapPin className="w-5 h-5 mr-2" />
            Xem bản đồ
          </Link>
          <Link
            href="/analytics"
            className="inline-flex items-center px-4 py-2 bg-white/20 text-white rounded-lg hover:bg-white/30 transition-colors font-medium"
          >
            <BarChart3 className="w-5 h-5 mr-2" />
            Xem thống kê
          </Link>
        </div>
      </div>
    </div>
  );
}
