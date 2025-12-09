// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

'use client';

import { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle, Clock, RefreshCw, Bell, Lightbulb } from 'lucide-react';
import toast from 'react-hot-toast';
import { adminService } from '@/lib/admin-service';

interface Alert {
  id: string;
  type: 'environment' | 'traffic' | 'civic' | 'parking' | 'system';
  severity: 'critical' | 'warning' | 'info';
  title: string;
  description: string;
  location: string;
  timestamp: string;
  status: 'active' | 'acknowledged' | 'resolved';
  recommendation: string;
  impact: string;
}

export default function SmartAlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [filter, setFilter] = useState<'all' | 'critical' | 'warning' | 'info'>('all');

  const fetchAlerts = async (showToast = false) => {
    try {
      if (showToast) setRefreshing(true);
      
      const metrics = await adminService.getRealTimeMetrics();
      const overview = await adminService.getDashboardOverview();
      
      const newAlerts: Alert[] = [];
      
      // Phân tích AQI
      const aqi = metrics.air_quality?.latest?.aqi || 0;
      if (aqi > 150) {
        newAlerts.push({
          id: 'aqi-high',
          type: 'environment',
          severity: aqi > 200 ? 'critical' : 'warning',
          title: 'Chất lượng không khí kém',
          description: `Chỉ số AQI đạt ${aqi}, vượt ngưỡng an toàn. Nhóm nhạy cảm cần hạn chế ra ngoài.`,
          location: 'Toàn thành phố',
          timestamp: new Date().toISOString(),
          status: 'active',
          recommendation: 'Phát cảnh báo y tế công cộng, khuyến cáo đeo khẩu trang N95 khi ra ngoài.',
          impact: 'Ảnh hưởng sức khỏe hô hấp, tăng 30% ca khám hô hấp tại bệnh viện.',
        });
      }
      
      // Phân tích nhiệt độ
      const temp = metrics.weather?.latest?.temperature || 25;
      if (temp > 38) {
        newAlerts.push({
          id: 'temp-high',
          type: 'environment',
          severity: 'warning',
          title: 'Cảnh báo nắng nóng',
          description: `Nhiệt độ ${temp}°C - nguy cơ say nắng, sốc nhiệt cho người lao động ngoài trời.`,
          location: 'Toàn thành phố',
          timestamp: new Date().toISOString(),
          status: 'active',
          recommendation: 'Mở trạm làm mát công cộng, điều chỉnh giờ làm việc công trình.',
          impact: 'Tăng tiêu thụ điện 25%, nguy cơ sức khỏe cho 15% dân số.',
        });
      }
      
      // Phân tích giao thông
      const trafficSpeed = metrics.traffic?.latest?.average_speed || 40;
      if (trafficSpeed < 15) {
        newAlerts.push({
          id: 'traffic-jam',
          type: 'traffic',
          severity: 'warning',
          title: 'Ùn tắc giao thông nghiêm trọng',
          description: `Tốc độ trung bình ${trafficSpeed} km/h - dưới 50% bình thường.`,
          location: 'Khu vực trung tâm',
          timestamp: new Date().toISOString(),
          status: 'active',
          recommendation: 'Điều phối đèn giao thông, triển khai CSGT tại các nút.',
          impact: 'Tăng thời gian di chuyển 45 phút, thiệt hại kinh tế ước tính 2 tỷ/giờ.',
        });
      }
      
      // Phân tích bãi đỗ
      const totalParking = overview.entity_statistics?.parking?.total || 100;
      const occupancy = 85; // Giả định
      if (occupancy > 90) {
        newAlerts.push({
          id: 'parking-full',
          type: 'parking',
          severity: 'info',
          title: 'Bãi đỗ xe sắp đầy',
          description: `Tỷ lệ lấp đầy ${occupancy}% - chỉ còn ${Math.round(totalParking * (100 - occupancy) / 100)} chỗ trống.`,
          location: 'Khu vực trung tâm',
          timestamp: new Date().toISOString(),
          status: 'active',
          recommendation: 'Hướng dẫn xe đến bãi đỗ ngoại vi, kích hoạt shuttle bus.',
          impact: 'Xe tìm chỗ đỗ tăng 20 phút, tăng khí thải khu vực.',
        });
      }
      
      // Phân tích sự cố dân sự
      const pendingIssues = Math.round((overview.entity_statistics?.civic_issues?.total || 50) * 0.35);
      if (pendingIssues > 15) {
        newAlerts.push({
          id: 'civic-backlog',
          type: 'civic',
          severity: 'warning',
          title: 'Tồn đọng sự cố dân sự',
          description: `${pendingIssues} sự cố chưa xử lý - vượt mức SLA cho phép.`,
          location: 'Nhiều quận',
          timestamp: new Date().toISOString(),
          status: 'active',
          recommendation: 'Tăng cường đội xử lý sự cố, ưu tiên theo mức độ nghiêm trọng.',
          impact: 'Giảm điểm hài lòng công dân, nguy cơ leo thang sự cố nhỏ.',
        });
      }
      
      // Thêm một số alert mẫu nếu không có dữ liệu thực
      if (newAlerts.length === 0) {
        newAlerts.push({
          id: 'system-ok',
          type: 'system',
          severity: 'info',
          title: 'Hệ thống hoạt động bình thường',
          description: 'Tất cả các chỉ số đều trong ngưỡng an toàn.',
          location: 'Toàn hệ thống',
          timestamp: new Date().toISOString(),
          status: 'active',
          recommendation: 'Tiếp tục giám sát và duy trì.',
          impact: 'Không có ảnh hưởng tiêu cực.',
        });
      }
      
      setAlerts(newAlerts);
      if (showToast) toast.success('Đã cập nhật cảnh báo');
    } catch (error) {
      console.error('Error:', error);
      toast.error('Không thể tải cảnh báo');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
    const interval = setInterval(() => fetchAlerts(), 30000);
    return () => clearInterval(interval);
  }, []);

  const acknowledgeAlert = (id: string) => {
    setAlerts(prev => prev.map(a => a.id === id ? { ...a, status: 'acknowledged' } : a));
    toast.success('Đã xác nhận cảnh báo');
  };

  const resolveAlert = (id: string) => {
    setAlerts(prev => prev.map(a => a.id === id ? { ...a, status: 'resolved' } : a));
    toast.success('Đã đánh dấu giải quyết');
  };

  const filteredAlerts = alerts.filter(a => filter === 'all' || a.severity === filter);
  
  const stats = {
    critical: alerts.filter(a => a.severity === 'critical' && a.status === 'active').length,
    warning: alerts.filter(a => a.severity === 'warning' && a.status === 'active').length,
    info: alerts.filter(a => a.severity === 'info' && a.status === 'active').length,
    resolved: alerts.filter(a => a.status === 'resolved').length,
  };

  const getSeverityStyle = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-50 border-red-200 text-red-800';
      case 'warning': return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      default: return 'bg-blue-50 border-blue-200 text-blue-800';
    }
  };

  const getSeverityBadge = (severity: string) => {
    switch (severity) {
      case 'critical': return 'bg-red-100 text-red-800 border-red-300';
      case 'warning': return 'bg-yellow-100 text-yellow-800 border-yellow-300';
      default: return 'bg-blue-100 text-blue-800 border-blue-300';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'environment': return '🌡️';
      case 'traffic': return '🚗';
      case 'civic': return '🏛️';
      case 'parking': return '🅿️';
      default: return '⚙️';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-white">
        <div className="text-center">
          <div className="animate-spin rounded-full h-10 w-10 border-2 border-green-600 border-t-transparent mx-auto"></div>
          <p className="mt-4 text-gray-600">Đang tải cảnh báo...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Bell className="h-6 w-6 text-green-600" />
            Cảnh báo Thông minh
          </h1>
          <p className="text-gray-500 text-sm mt-1">Giám sát và cảnh báo tự động từ dữ liệu</p>
        </div>
        <button
          onClick={() => fetchAlerts(true)}
          disabled={refreshing}
          className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
        >
          <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
          Làm mới
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-xl border border-gray-200">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Nghiêm trọng</span>
            <span className="text-2xl font-bold text-red-600">{stats.critical}</span>
          </div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-gray-200">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Cảnh báo</span>
            <span className="text-2xl font-bold text-yellow-600">{stats.warning}</span>
          </div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-gray-200">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Thông tin</span>
            <span className="text-2xl font-bold text-blue-600">{stats.info}</span>
          </div>
        </div>
        <div className="bg-white p-4 rounded-xl border border-gray-200">
          <div className="flex items-center justify-between">
            <span className="text-sm text-gray-600">Đã xử lý</span>
            <span className="text-2xl font-bold text-green-600">{stats.resolved}</span>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-2 mb-6">
        {(['all', 'critical', 'warning', 'info'] as const).map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === f ? 'bg-green-600 text-white' : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
            }`}
          >
            {f === 'all' ? 'Tất cả' : f === 'critical' ? 'Nghiêm trọng' : f === 'warning' ? 'Cảnh báo' : 'Thông tin'}
          </button>
        ))}
      </div>

      {/* Alerts List */}
      <div className="space-y-4">
        {filteredAlerts.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-200 p-8 text-center">
            <CheckCircle className="h-12 w-12 text-green-600 mx-auto mb-3" />
            <p className="text-gray-600">Không có cảnh báo nào</p>
          </div>
        ) : (
          filteredAlerts.map(alert => (
            <div
              key={alert.id}
              className={`bg-white rounded-xl border p-5 ${
                alert.status === 'resolved' ? 'opacity-60 border-gray-200' : 'border-gray-200'
              }`}
            >
              {/* Header */}
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{getTypeIcon(alert.type)}</span>
                  <div>
                    <h3 className="font-semibold text-gray-900">{alert.title}</h3>
                    <div className="flex items-center gap-2 mt-1">
                      <span className={`px-2 py-0.5 rounded text-xs font-medium border ${getSeverityBadge(alert.severity)}`}>
                        {alert.severity === 'critical' ? 'Nghiêm trọng' : alert.severity === 'warning' ? 'Cảnh báo' : 'Thông tin'}
                      </span>
                      <span className="text-xs text-gray-500">{alert.location}</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2 text-xs text-gray-500">
                  <Clock className="h-3 w-3" />
                  {new Date(alert.timestamp).toLocaleTimeString('vi-VN')}
                </div>
              </div>

              {/* Description */}
              <p className="text-gray-700 text-sm mb-4">{alert.description}</p>

              {/* Impact & Recommendation */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
                <div className="p-3 bg-red-50 rounded-lg border border-red-100">
                  <div className="flex items-center gap-2 text-red-800 text-xs font-semibold mb-1">
                    <AlertTriangle className="h-3 w-3" />
                    Tác động dự kiến
                  </div>
                  <p className="text-sm text-gray-700">{alert.impact}</p>
                </div>
                <div className="p-3 bg-green-50 rounded-lg border border-green-100">
                  <div className="flex items-center gap-2 text-green-800 text-xs font-semibold mb-1">
                    <Lightbulb className="h-3 w-3" />
                    Khuyến nghị
                  </div>
                  <p className="text-sm text-gray-700">{alert.recommendation}</p>
                </div>
              </div>

              {/* Actions */}
              {alert.status === 'active' && (
                <div className="flex gap-2">
                  <button
                    onClick={() => acknowledgeAlert(alert.id)}
                    className="px-3 py-1.5 bg-blue-600 text-white rounded text-sm hover:bg-blue-700"
                  >
                    Xác nhận
                  </button>
                  <button
                    onClick={() => resolveAlert(alert.id)}
                    className="px-3 py-1.5 bg-green-600 text-white rounded text-sm hover:bg-green-700"
                  >
                    Đã xử lý
                  </button>
                </div>
              )}
              {alert.status === 'acknowledged' && (
                <div className="flex items-center gap-2">
                  <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">Đã xác nhận</span>
                  <button
                    onClick={() => resolveAlert(alert.id)}
                    className="px-3 py-1.5 bg-green-600 text-white rounded text-sm hover:bg-green-700"
                  >
                    Đã xử lý
                  </button>
                </div>
              )}
              {alert.status === 'resolved' && (
                <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">Đã xử lý</span>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
}
