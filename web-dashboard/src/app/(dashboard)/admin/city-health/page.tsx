// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

'use client';

import { useEffect, useState } from 'react';
import { 
  Activity, TrendingUp, TrendingDown, Minus, RefreshCw, Wind, Car, Building, MapPin, Lightbulb,
  Download, BarChart3, Map, Layers
} from 'lucide-react';
import toast from 'react-hot-toast';
import { adminService } from '@/lib/admin-service';
import { DataFilters, ExportModal, ExportOptions, DISTRICTS } from '@/components/data-intelligence/DataFilters';

interface CityHealthData {
  overall_score: number;
  ward?: string;
  environmental_health: {
    score: number;
    aqi_status: string;
    aqi_value: number;
    trend: 'up' | 'down' | 'stable';
    temperature: number;
    humidity: number;
  };
  traffic_efficiency: {
    score: number;
    congestion_level: string;
    average_speed: number;
    trend: 'up' | 'down' | 'stable';
  };
  civic_responsiveness: {
    score: number;
    pending_issues: number;
    resolution_rate: number;
    avg_resolution_time: number;
    trend: 'up' | 'down' | 'stable';
  };
  parking_utilization: {
    score: number;
    occupancy_rate: number;
    available_spots: number;
    trend: 'up' | 'down' | 'stable';
  };
  last_updated: string;
}

interface AIInsight {
  summary: string;
  recommendations: string[];
  risks: string[];
}

// Simulated ward-specific data generator
const generateWardData = (wardName: string, baseData: CityHealthData): CityHealthData => {
  // Create deterministic but varied data based on ward name hash
  const hash = wardName.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  const variation = (hash % 30) - 15; // -15 to +15 variation
  
  const clamp = (val: number, min: number, max: number) => Math.max(min, Math.min(max, val));
  
  return {
    ...baseData,
    ward: wardName,
    overall_score: clamp(baseData.overall_score + variation, 30, 95),
    environmental_health: {
      ...baseData.environmental_health,
      score: clamp(baseData.environmental_health.score + (hash % 20) - 10, 30, 100),
      aqi_value: clamp(baseData.environmental_health.aqi_value + (hash % 40) - 20, 20, 200),
      temperature: clamp(baseData.environmental_health.temperature + (hash % 6) - 3, 18, 38),
    },
    traffic_efficiency: {
      ...baseData.traffic_efficiency,
      score: clamp(baseData.traffic_efficiency.score + (hash % 25) - 12, 20, 100),
      average_speed: clamp(baseData.traffic_efficiency.average_speed + (hash % 20) - 10, 15, 55),
    },
    civic_responsiveness: {
      ...baseData.civic_responsiveness,
      score: clamp(baseData.civic_responsiveness.score + (hash % 15) - 7, 40, 100),
      pending_issues: Math.max(0, baseData.civic_responsiveness.pending_issues + (hash % 10) - 5),
    },
    parking_utilization: {
      ...baseData.parking_utilization,
      score: clamp(baseData.parking_utilization.score + (hash % 20) - 10, 30, 100),
      occupancy_rate: clamp(baseData.parking_utilization.occupancy_rate + (hash % 20) - 10, 30, 95),
    },
  };
};

export default function CityHealthPage() {
  const [healthData, setHealthData] = useState<CityHealthData | null>(null);
  const [wardHealthData, setWardHealthData] = useState<CityHealthData[]>([]);
  const [aiInsight, setAiInsight] = useState<AIInsight | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [analyzingAI, setAnalyzingAI] = useState(false);
  
  // Filters
  const [selectedWards, setSelectedWards] = useState<string[]>([]);
  const [timeRange, setTimeRange] = useState('today');
  const [customDateRange, setCustomDateRange] = useState({ start: '', end: '' });
  const [metricType, setMetricType] = useState('all');
  
  // Export
  const [showExportModal, setShowExportModal] = useState(false);
  
  // View mode
  const [viewMode, setViewMode] = useState<'overview' | 'comparison' | 'heatmap'>('overview');

  const fetchHealthData = async (showToast = false) => {
    try {
      if (showToast) setRefreshing(true);
      
      const metrics = await adminService.getRealTimeMetrics();
      const overview = await adminService.getDashboardOverview();
      
      // Tính điểm Môi trường (0-100)
      const aqi = metrics.air_quality?.latest?.aqi || 0;
      const temp = metrics.weather?.latest?.temperature || 25;
      const humidity = metrics.weather?.latest?.humidity || 60;
      
      let aqiScore = 100;
      if (aqi > 300) aqiScore = 0;
      else if (aqi > 200) aqiScore = 20;
      else if (aqi > 150) aqiScore = 40;
      else if (aqi > 100) aqiScore = 60;
      else if (aqi > 50) aqiScore = 80;
      
      const tempScore = temp >= 20 && temp <= 28 ? 100 : Math.max(0, 100 - Math.abs(temp - 24) * 5);
      const humidityScore = humidity >= 40 && humidity <= 70 ? 100 : Math.max(0, 100 - Math.abs(humidity - 55) * 2);
      const environmentalScore = Math.round((aqiScore * 0.6 + tempScore * 0.2 + humidityScore * 0.2));
      
      // Tính điểm Giao thông
      const trafficSpeed = metrics.traffic?.latest?.average_speed || 40;
      const trafficScore = Math.min(100, Math.round((trafficSpeed / 60) * 100));
      
      // Tính điểm Phản hồi dân sự
      const totalCivicIssues = overview.entity_statistics?.civic_issues?.total || 0;
      const pendingIssues = Math.round(totalCivicIssues * 0.3);
      const resolutionRate = totalCivicIssues > 0 ? Math.round((1 - pendingIssues / totalCivicIssues) * 100) : 100;
      const civicScore = resolutionRate;
      
      // Tính điểm Bãi đỗ xe
      const totalParking = overview.entity_statistics?.parking?.total || 100;
      const availableParking = Math.round(totalParking * 0.4);
      const occupancyRate = Math.round((1 - availableParking / totalParking) * 100);
      const parkingScore = occupancyRate > 90 ? 50 : (occupancyRate < 30 ? 70 : 100);
      
      // Điểm tổng
      const overallScore = Math.round(
        environmentalScore * 0.35 +
        trafficScore * 0.25 +
        civicScore * 0.25 +
        parkingScore * 0.15
      );
      
      const data: CityHealthData = {
        overall_score: overallScore,
        environmental_health: {
          score: environmentalScore,
          aqi_status: aqi <= 50 ? 'Tốt' : aqi <= 100 ? 'Trung bình' : aqi <= 150 ? 'Kém' : 'Xấu',
          aqi_value: aqi,
          trend: 'stable',
          temperature: temp,
          humidity: humidity,
        },
        traffic_efficiency: {
          score: trafficScore,
          congestion_level: trafficScore > 70 ? 'Thấp' : trafficScore > 40 ? 'Trung bình' : 'Cao',
          average_speed: trafficSpeed,
          trend: 'stable',
        },
        civic_responsiveness: {
          score: civicScore,
          pending_issues: pendingIssues,
          resolution_rate: resolutionRate,
          avg_resolution_time: 3.5,
          trend: 'up',
        },
        parking_utilization: {
          score: parkingScore,
          occupancy_rate: occupancyRate,
          available_spots: availableParking,
          trend: 'stable',
        },
        last_updated: new Date().toISOString(),
      };
      
      setHealthData(data);
      
      // Generate ward-specific data
      if (selectedWards.length > 0) {
        const wardData = selectedWards.map(ward => generateWardData(ward, data));
        setWardHealthData(wardData);
      } else {
        setWardHealthData([]);
      }
      
      // Tạo AI insight dựa trên dữ liệu thực
      generateAIInsight(data);
      
      if (showToast) toast.success('Đã cập nhật dữ liệu');
    } catch (error) {
      console.error('Lỗi:', error);
      toast.error('Không thể tải dữ liệu');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const generateAIInsight = async (data: CityHealthData) => {
    setAnalyzingAI(true);
    try {
      // Phân tích dựa trên dữ liệu thực
      const recommendations: string[] = [];
      const risks: string[] = [];
      
      // Phân tích môi trường
      if (data.environmental_health.aqi_value > 100) {
        risks.push(`Chất lượng không khí kém (AQI: ${data.environmental_health.aqi_value}) - cần cảnh báo người dân`);
        recommendations.push('Khuyến cáo người dân hạn chế hoạt động ngoài trời');
      }
      if (data.environmental_health.temperature > 35) {
        risks.push(`Nhiệt độ cao (${data.environmental_health.temperature}°C) - nguy cơ say nắng`);
        recommendations.push('Mở các trạm làm mát công cộng');
      }
      
      // Phân tích giao thông
      if (data.traffic_efficiency.score < 50) {
        risks.push('Giao thông ùn tắc nghiêm trọng');
        recommendations.push('Điều phối đèn tín hiệu giao thông động');
        recommendations.push('Triển khai cảnh sát giao thông tại các nút thắt');
      }
      
      // Phân tích sự cố dân sự
      if (data.civic_responsiveness.pending_issues > 20) {
        risks.push(`${data.civic_responsiveness.pending_issues} sự cố chưa xử lý`);
        recommendations.push('Tăng cường đội ngũ xử lý sự cố');
      }
      
      // Phân tích bãi đỗ
      if (data.parking_utilization.occupancy_rate > 85) {
        risks.push('Bãi đỗ xe gần đầy');
        recommendations.push('Hướng dẫn xe đến bãi đỗ ngoại vi');
      }
      
      // Tổng hợp
      let summary = '';
      if (data.overall_score >= 80) {
        summary = `Đô thị đang hoạt động TỐT với điểm ${data.overall_score}/100. Các chỉ số chính đều trong ngưỡng an toàn.`;
      } else if (data.overall_score >= 60) {
        summary = `Đô thị ở mức TRUNG BÌNH với điểm ${data.overall_score}/100. Cần chú ý một số vấn đề.`;
      } else {
        summary = `Đô thị CẦN CẢI THIỆN với điểm ${data.overall_score}/100. Nhiều vấn đề cần giải quyết ngay.`;
      }
      
      if (recommendations.length === 0) {
        recommendations.push('Duy trì giám sát liên tục');
        recommendations.push('Chuẩn bị phương án dự phòng');
      }
      
      setAiInsight({ summary, recommendations, risks });
    } catch (error) {
      console.error('AI Error:', error);
    } finally {
      setAnalyzingAI(false);
    }
  };

  useEffect(() => {
    fetchHealthData();
    const interval = setInterval(() => fetchHealthData(), 60000);
    return () => clearInterval(interval);
  }, [selectedWards]); // Re-fetch when selected wards change
  
  // Handle export
  const handleExport = (format: string, options: ExportOptions) => {
    const exportData = {
      generated_at: new Date().toISOString(),
      time_range: timeRange,
      custom_date_range: customDateRange,
      selected_wards: selectedWards.length > 0 ? selectedWards : ['Toàn TP. Hà Nội'],
      metric_type: metricType,
      overall_health: healthData,
      ward_breakdown: wardHealthData,
      ai_insights: options.includeRecommendations ? aiInsight : null,
    };
    
    if (format === 'json') {
      const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `city-health-report-${new Date().toISOString().split('T')[0]}.json`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success('Đã xuất báo cáo JSON');
    } else if (format === 'csv') {
      // Create CSV for ward data
      const headers = ['Phường/Xã', 'Điểm tổng', 'Môi trường', 'Giao thông', 'Phản hồi', 'Bãi đỗ xe'];
      const rows = wardHealthData.length > 0 
        ? wardHealthData.map(w => [
            w.ward || 'Toàn TP',
            w.overall_score,
            w.environmental_health.score,
            w.traffic_efficiency.score,
            w.civic_responsiveness.score,
            w.parking_utilization.score
          ])
        : [[
            'Toàn TP. Hà Nội',
            healthData?.overall_score,
            healthData?.environmental_health.score,
            healthData?.traffic_efficiency.score,
            healthData?.civic_responsiveness.score,
            healthData?.parking_utilization.score
          ]];
      
      const csvContent = [headers.join(','), ...rows.map(r => r.join(','))].join('\n');
      const blob = new Blob([csvContent], { type: 'text/csv' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `city-health-report-${new Date().toISOString().split('T')[0]}.csv`;
      a.click();
      URL.revokeObjectURL(url);
      toast.success('Đã xuất báo cáo CSV');
    } else {
      toast.success(`Đang chuẩn bị báo cáo ${format.toUpperCase()}...`);
      // In a real app, this would call an API to generate PDF/Excel
    }
    
    setShowExportModal(false);
  };

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-green-600 dark:text-green-500';
    if (score >= 60) return 'text-yellow-600 dark:text-yellow-500';
    if (score >= 40) return 'text-orange-600 dark:text-orange-500';
    return 'text-red-600 dark:text-red-500';
  };

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'bg-green-50 dark:bg-green-950/30 border-green-200 dark:border-green-800';
    if (score >= 60) return 'bg-yellow-50 dark:bg-yellow-950/30 border-yellow-200 dark:border-yellow-800';
    if (score >= 40) return 'bg-orange-50 dark:bg-orange-950/30 border-orange-200 dark:border-orange-800';
    return 'bg-red-50 dark:bg-red-950/30 border-red-200 dark:border-red-800';
  };

  const TrendIcon = ({ trend }: { trend: 'up' | 'down' | 'stable' }) => {
    if (trend === 'up') return <TrendingUp className="h-4 w-4 text-green-600" />;
    if (trend === 'down') return <TrendingDown className="h-4 w-4 text-red-600" />;
    return <Minus className="h-4 w-4 text-gray-400" />;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-10 w-10 border-2 border-green-600 border-t-transparent mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Đang tải dữ liệu...</p>
        </div>
      </div>
    );
  }

  if (!healthData) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <p className="text-muted-foreground">Không có dữ liệu</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Activity className="h-6 w-6 text-green-600 dark:text-green-500" />
            Giám sát Sức khỏe Đô thị
          </h1>
          <p className="text-muted-foreground text-sm mt-1">
            Cập nhật: {new Date(healthData.last_updated).toLocaleString('vi-VN')}
            {selectedWards.length > 0 && (
              <span className="ml-2 text-green-600">• {selectedWards.length} phường được chọn</span>
            )}
          </p>
        </div>
        <div className="flex items-center gap-2">
          {/* View Mode Toggle */}
          <div className="flex items-center bg-muted rounded-lg p-1">
            <button
              onClick={() => setViewMode('overview')}
              className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                viewMode === 'overview' ? 'bg-card shadow text-foreground' : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <BarChart3 className="h-4 w-4" />
            </button>
            <button
              onClick={() => setViewMode('comparison')}
              className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                viewMode === 'comparison' ? 'bg-card shadow text-foreground' : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <Layers className="h-4 w-4" />
            </button>
            <button
              onClick={() => setViewMode('heatmap')}
              className={`px-3 py-1.5 text-sm rounded-md transition-colors ${
                viewMode === 'heatmap' ? 'bg-card shadow text-foreground' : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              <Map className="h-4 w-4" />
            </button>
          </div>
          
          {/* Export Button */}
          <button
            onClick={() => setShowExportModal(true)}
            className="flex items-center gap-2 px-4 py-2 border border-border rounded-lg hover:bg-muted transition-colors"
          >
            <Download className="h-4 w-4" />
            Xuất báo cáo
          </button>
          
          {/* Refresh Button */}
          <button
            onClick={() => fetchHealthData(true)}
            disabled={refreshing}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
            Làm mới
          </button>
        </div>
      </div>
      
      {/* Data Filters */}
      <div className="mb-6">
        <DataFilters
          selectedWards={selectedWards}
          onWardsChange={setSelectedWards}
          timeRange={timeRange}
          onTimeRangeChange={setTimeRange}
          customDateRange={customDateRange}
          onCustomDateRangeChange={setCustomDateRange}
          metricType={metricType}
          onMetricTypeChange={setMetricType}
          maxWards={10}
        />
      </div>

      {/* Điểm tổng */}
      <div className={`p-6 rounded-xl border-2 mb-6 ${getScoreBg(healthData.overall_score)}`}>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-muted-foreground mb-1">ĐIỂM SỨC KHỎE ĐÔ THỊ</p>
            <div className={`text-5xl font-bold ${getScoreColor(healthData.overall_score)}`}>
              {healthData.overall_score}
              <span className="text-2xl text-muted-foreground">/100</span>
            </div>
          </div>
          <div className="text-right">
            <span className={`inline-block px-3 py-1 rounded-full text-sm font-medium ${
              healthData.overall_score >= 80 ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300' :
              healthData.overall_score >= 60 ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300' :
              'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-300'
            }`}>
              {healthData.overall_score >= 80 ? 'Tốt' : healthData.overall_score >= 60 ? 'Trung bình' : 'Cần cải thiện'}
            </span>
          </div>
        </div>
      </div>

      {/* 4 chỉ số chính */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {/* Môi trường */}
        <div className="bg-card p-5 rounded-xl border border-border">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Wind className="h-5 w-5 text-green-600 dark:text-green-500" />
              <span className="font-medium text-foreground">Môi trường</span>
            </div>
            <TrendIcon trend={healthData.environmental_health.trend} />
          </div>
          <div className={`text-3xl font-bold mb-2 ${getScoreColor(healthData.environmental_health.score)}`}>
            {healthData.environmental_health.score}
          </div>
          <div className="space-y-1 text-sm text-muted-foreground">
            <div className="flex justify-between">
              <span>AQI:</span>
              <span className="font-medium">{healthData.environmental_health.aqi_value} ({healthData.environmental_health.aqi_status})</span>
            </div>
            <div className="flex justify-between">
              <span>Nhiệt độ:</span>
              <span className="font-medium">{healthData.environmental_health.temperature}°C</span>
            </div>
            <div className="flex justify-between">
              <span>Độ ẩm:</span>
              <span className="font-medium">{healthData.environmental_health.humidity}%</span>
            </div>
          </div>
        </div>

        {/* Giao thông */}
        <div className="bg-card p-5 rounded-xl border border-border">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Car className="h-5 w-5 text-green-600 dark:text-green-500" />
              <span className="font-medium text-foreground">Giao thông</span>
            </div>
            <TrendIcon trend={healthData.traffic_efficiency.trend} />
          </div>
          <div className={`text-3xl font-bold mb-2 ${getScoreColor(healthData.traffic_efficiency.score)}`}>
            {healthData.traffic_efficiency.score}
          </div>
          <div className="space-y-1 text-sm text-muted-foreground">
            <div className="flex justify-between">
              <span>Ùn tắc:</span>
              <span className="font-medium">{healthData.traffic_efficiency.congestion_level}</span>
            </div>
            <div className="flex justify-between">
              <span>Tốc độ TB:</span>
              <span className="font-medium">{healthData.traffic_efficiency.average_speed} km/h</span>
            </div>
          </div>
        </div>

        {/* Phản hồi */}
        <div className="bg-card p-5 rounded-xl border border-border">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <Building className="h-5 w-5 text-green-600 dark:text-green-500" />
              <span className="font-medium text-foreground">Phản hồi sự cố</span>
            </div>
            <TrendIcon trend={healthData.civic_responsiveness.trend} />
          </div>
          <div className={`text-3xl font-bold mb-2 ${getScoreColor(healthData.civic_responsiveness.score)}`}>
            {healthData.civic_responsiveness.score}
          </div>
          <div className="space-y-1 text-sm text-muted-foreground">
            <div className="flex justify-between">
              <span>Chờ xử lý:</span>
              <span className="font-medium">{healthData.civic_responsiveness.pending_issues}</span>
            </div>
            <div className="flex justify-between">
              <span>Tỷ lệ giải quyết:</span>
              <span className="font-medium">{healthData.civic_responsiveness.resolution_rate}%</span>
            </div>
          </div>
        </div>

        {/* Bãi đỗ xe */}
        <div className="bg-card p-5 rounded-xl border border-border">
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <MapPin className="h-5 w-5 text-green-600 dark:text-green-500" />
              <span className="font-medium text-foreground">Bãi đỗ xe</span>
            </div>
            <TrendIcon trend={healthData.parking_utilization.trend} />
          </div>
          <div className={`text-3xl font-bold mb-2 ${getScoreColor(healthData.parking_utilization.score)}`}>
            {healthData.parking_utilization.score}
          </div>
          <div className="space-y-1 text-sm text-muted-foreground">
            <div className="flex justify-between">
              <span>Đã đỗ:</span>
              <span className="font-medium">{healthData.parking_utilization.occupancy_rate}%</span>
            </div>
            <div className="flex justify-between">
              <span>Còn trống:</span>
              <span className="font-medium">{healthData.parking_utilization.available_spots} chỗ</span>
            </div>
          </div>
        </div>
      </div>

      {/* AI Insights */}
      <div className="bg-card rounded-xl border border-border p-6">
        <div className="flex items-center gap-2 mb-4">
          <Lightbulb className="h-5 w-5 text-green-600 dark:text-green-500" />
          <h2 className="text-lg font-semibold text-foreground">Phân tích & Khuyến nghị</h2>
          {analyzingAI && <span className="text-sm text-muted-foreground">(Đang phân tích...)</span>}
        </div>
        
        {aiInsight && (
          <div className="space-y-4">
            {/* Tổng quan */}
            <div className="p-4 bg-muted/50 rounded-lg border border-border">
              <p className="text-foreground">{aiInsight.summary}</p>
            </div>

            {/* Rủi ro */}
            {aiInsight.risks.length > 0 && (
              <div>
                <h3 className="text-sm font-semibold text-red-600 dark:text-red-500 mb-2">Vấn đề cần chú ý:</h3>
                <ul className="space-y-1">
                  {aiInsight.risks.map((risk, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-foreground">
                      <span className="w-1.5 h-1.5 rounded-full bg-red-500 mt-2 flex-shrink-0"></span>
                      {risk}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Khuyến nghị */}
            <div>
              <h3 className="text-sm font-semibold text-green-600 dark:text-green-500 mb-2">Khuyến nghị hành động:</h3>
              <ul className="space-y-1">
                {aiInsight.recommendations.map((rec, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-foreground">
                    <span className="w-1.5 h-1.5 rounded-full bg-green-500 mt-2 flex-shrink-0"></span>
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
      
      {/* Ward Comparison Section - shown when wards are selected */}
      {viewMode === 'comparison' && wardHealthData.length > 0 && (
        <div className="mt-6 bg-card rounded-xl border border-border p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Layers className="h-5 w-5 text-green-600" />
              <h2 className="text-lg font-semibold text-foreground">So sánh theo Phường/Xã</h2>
            </div>
            <span className="text-sm text-muted-foreground">{wardHealthData.length} phường đang so sánh</span>
          </div>
          
          {/* Comparison Table */}
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-border">
                  <th className="text-left py-3 px-2 font-medium text-muted-foreground">Phường/Xã</th>
                  <th className="text-center py-3 px-2 font-medium text-muted-foreground">Tổng</th>
                  <th className="text-center py-3 px-2 font-medium text-muted-foreground">
                    <Wind className="h-4 w-4 inline mr-1" />
                    Môi trường
                  </th>
                  <th className="text-center py-3 px-2 font-medium text-muted-foreground">
                    <Car className="h-4 w-4 inline mr-1" />
                    Giao thông
                  </th>
                  <th className="text-center py-3 px-2 font-medium text-muted-foreground">
                    <Building className="h-4 w-4 inline mr-1" />
                    Phản hồi
                  </th>
                  <th className="text-center py-3 px-2 font-medium text-muted-foreground">
                    <MapPin className="h-4 w-4 inline mr-1" />
                    Bãi đỗ
                  </th>
                  <th className="text-center py-3 px-2 font-medium text-muted-foreground">AQI</th>
                </tr>
              </thead>
              <tbody>
                {wardHealthData.map((ward, idx) => (
                  <tr key={idx} className="border-b border-border/50 hover:bg-muted/30">
                    <td className="py-3 px-2 font-medium text-foreground">
                      {ward.ward?.replace('Phường ', 'P. ').replace('Xã ', 'X. ')}
                    </td>
                    <td className="py-3 px-2 text-center">
                      <span className={`font-bold ${getScoreColor(ward.overall_score)}`}>
                        {ward.overall_score}
                      </span>
                    </td>
                    <td className="py-3 px-2 text-center">
                      <span className={getScoreColor(ward.environmental_health.score)}>
                        {ward.environmental_health.score}
                      </span>
                    </td>
                    <td className="py-3 px-2 text-center">
                      <span className={getScoreColor(ward.traffic_efficiency.score)}>
                        {ward.traffic_efficiency.score}
                      </span>
                    </td>
                    <td className="py-3 px-2 text-center">
                      <span className={getScoreColor(ward.civic_responsiveness.score)}>
                        {ward.civic_responsiveness.score}
                      </span>
                    </td>
                    <td className="py-3 px-2 text-center">
                      <span className={getScoreColor(ward.parking_utilization.score)}>
                        {ward.parking_utilization.score}
                      </span>
                    </td>
                    <td className="py-3 px-2 text-center text-muted-foreground">
                      {ward.environmental_health.aqi_value}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {/* Score Legend */}
          <div className="mt-4 flex items-center gap-4 text-xs text-muted-foreground">
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded bg-green-500"></span>
              Tốt (≥80)
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded bg-yellow-500"></span>
              TB (60-79)
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded bg-orange-500"></span>
              Kém (40-59)
            </span>
            <span className="flex items-center gap-1">
              <span className="w-3 h-3 rounded bg-red-500"></span>
              Xấu (&lt;40)
            </span>
          </div>
        </div>
      )}
      
      {/* Heatmap View - District Overview */}
      {viewMode === 'heatmap' && (
        <div className="mt-6 bg-card rounded-xl border border-border p-6">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Map className="h-5 w-5 text-green-600" />
              <h2 className="text-lg font-semibold text-foreground">Bản đồ Sức khỏe theo Quận</h2>
            </div>
          </div>
          
          {/* District Grid as Heatmap */}
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {Object.entries(DISTRICTS).map(([district, wards]) => {
              // Calculate average score for district
              const districtScore = Math.round(
                wards.reduce((acc, ward) => {
                  const hash = ward.split('').reduce((a, c) => a + c.charCodeAt(0), 0);
                  return acc + Math.min(95, Math.max(35, healthData.overall_score + (hash % 30) - 15));
                }, 0) / wards.length
              );
              
              return (
                <div
                  key={district}
                  className={`p-4 rounded-lg border cursor-pointer transition-all hover:scale-105 ${
                    districtScore >= 80 ? 'bg-green-100 dark:bg-green-900/30 border-green-300 dark:border-green-700' :
                    districtScore >= 60 ? 'bg-yellow-100 dark:bg-yellow-900/30 border-yellow-300 dark:border-yellow-700' :
                    districtScore >= 40 ? 'bg-orange-100 dark:bg-orange-900/30 border-orange-300 dark:border-orange-700' :
                    'bg-red-100 dark:bg-red-900/30 border-red-300 dark:border-red-700'
                  }`}
                  onClick={() => {
                    setSelectedWards(wards.slice(0, 10));
                    setViewMode('comparison');
                  }}
                >
                  <h3 className="font-semibold text-foreground mb-1">{district}</h3>
                  <div className={`text-2xl font-bold ${getScoreColor(districtScore)}`}>
                    {districtScore}
                  </div>
                  <p className="text-xs text-muted-foreground mt-1">{wards.length} phường</p>
                </div>
              );
            })}
          </div>
          
          <p className="mt-4 text-sm text-muted-foreground text-center flex items-center justify-center gap-2">
            <Lightbulb className="h-4 w-4 text-amber-500" />
            Click vào quận để xem so sánh chi tiết các phường
          </p>
        </div>
      )}
      
      {/* No wards selected hint for comparison mode */}
      {viewMode === 'comparison' && wardHealthData.length === 0 && (
        <div className="mt-6 bg-muted/30 rounded-xl border border-dashed border-border p-8 text-center">
          <Layers className="h-10 w-10 text-muted-foreground mx-auto mb-3" />
          <h3 className="text-lg font-medium text-foreground mb-2">Chọn phường để so sánh</h3>
          <p className="text-muted-foreground text-sm max-w-md mx-auto">
            Sử dụng bộ lọc &ldquo;Phường/Xã&rdquo; ở trên để chọn tối đa 10 phường muốn so sánh.
            Hoặc chuyển sang chế độ &ldquo;Bản đồ nhiệt&rdquo; và click vào quận.
          </p>
        </div>
      )}
      
      {/* Export Modal */}
      <ExportModal
        isOpen={showExportModal}
        onClose={() => setShowExportModal(false)}
        onExport={handleExport}
        selectedWards={selectedWards}
        timeRange={timeRange}
      />
    </div>
  );
}
