// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

'use client';

import { useEffect, useState, useMemo } from 'react';
import { BarChart3, RefreshCw, Download, TrendingUp, Clock, MapPin, Grid3X3 } from 'lucide-react';
import toast from 'react-hot-toast';
import { adminService } from '@/lib/admin-service';
import { DataFilters, HANOI_WARDS, DISTRICTS } from '@/components/data-intelligence/DataFilters';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface WardData {
  ward: string;
  district: string;
  aqi_score: number;
  traffic_score: number;
  civic_score: number;
  parking_score: number;
}

interface TemporalData {
  hour: string;
  traffic: number;
  parking: number;
}

// Helper to get district from ward name
const getDistrictForWard = (wardName: string): string => {
  for (const [district, wards] of Object.entries(DISTRICTS)) {
    if (wards.includes(wardName)) return district;
  }
  return 'Không xác định';
};

// Generate deterministic ward data based on ward name
const generateWardScore = (wardName: string, baseScore: number, variance: number): number => {
  const hash = wardName.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0);
  const variation = (hash % (variance * 2)) - variance;
  return Math.max(20, Math.min(100, Math.round(baseScore + variation)));
};

export default function DataInsightsPage() {
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [selectedTab, setSelectedTab] = useState<'correlation' | 'wards' | 'temporal' | 'matrix'>('correlation');
  
  // Filters
  const [selectedWards, setSelectedWards] = useState<string[]>([]);
  const [timeRange, setTimeRange] = useState('today');
  const [customDateRange, setCustomDateRange] = useState({ start: '', end: '' });
  const [metricType, setMetricType] = useState('all');
  
  // Data
  const [correlationData, setCorrelationData] = useState<any[]>([]);
  const [allWardData, setAllWardData] = useState<WardData[]>([]);
  const [temporalData, setTemporalData] = useState<TemporalData[]>([]);
  const [insights, setInsights] = useState<string[]>([]);

  // Filtered ward data based on selection
  const displayWardData = useMemo(() => {
    if (selectedWards.length === 0) {
      // Show district averages when no specific wards selected
      const districtAverages: WardData[] = [];
      for (const [district, wards] of Object.entries(DISTRICTS)) {
        const districtWards = allWardData.filter(w => wards.includes(w.ward));
        if (districtWards.length > 0) {
          districtAverages.push({
            ward: district,
            district: district,
            aqi_score: Math.round(districtWards.reduce((s, w) => s + w.aqi_score, 0) / districtWards.length),
            traffic_score: Math.round(districtWards.reduce((s, w) => s + w.traffic_score, 0) / districtWards.length),
            civic_score: Math.round(districtWards.reduce((s, w) => s + w.civic_score, 0) / districtWards.length),
            parking_score: Math.round(districtWards.reduce((s, w) => s + w.parking_score, 0) / districtWards.length),
          });
        }
      }
      return districtAverages;
    }
    return allWardData.filter(w => selectedWards.includes(w.ward));
  }, [allWardData, selectedWards]);

  const fetchData = async (showToast = false) => {
    try {
      if (showToast) setRefreshing(true);
      
      const metrics = await adminService.getRealTimeMetrics();
      
      const baseAqi = metrics.air_quality?.latest?.aqi || 75;
      const baseTemp = metrics.weather?.latest?.temperature || 28;
      
      // Dữ liệu tương quan Thời tiết - AQI (24h)
      const correlation = [];
      for (let i = 0; i < 24; i++) {
        const temp = baseTemp + Math.sin(i * 0.3) * 5 + (Math.random() - 0.5) * 3;
        const aqi = baseAqi + (temp - baseTemp) * 2.5 + Math.random() * 15;
        correlation.push({
          hour: `${i.toString().padStart(2, '0')}:00`,
          temperature: Math.round(temp * 10) / 10,
          aqi: Math.round(aqi),
        });
      }
      setCorrelationData(correlation);
      
      // Tạo dữ liệu cho TẤT CẢ 126 phường
      const wardData: WardData[] = HANOI_WARDS.map(ward => ({
        ward,
        district: getDistrictForWard(ward),
        aqi_score: generateWardScore(ward, 72, 20),
        traffic_score: generateWardScore(ward, 55, 25),
        civic_score: generateWardScore(ward, 80, 15),
        parking_score: generateWardScore(ward, 65, 20),
      }));
      setAllWardData(wardData);
      
      // Dữ liệu theo thời gian trong ngày
      const temporal: TemporalData[] = [];
      for (let h = 0; h < 24; h++) {
        const isRush = (h >= 7 && h <= 9) || (h >= 17 && h <= 19);
        temporal.push({
          hour: `${h.toString().padStart(2, '0')}:00`,
          traffic: isRush ? 75 + Math.random() * 20 : 25 + Math.random() * 30,
          parking: isRush ? 85 + Math.random() * 10 : 40 + Math.random() * 25,
        });
      }
      setTemporalData(temporal);
      
      // Phân tích insights
      const newInsights: string[] = [];
      
      // Best/Worst wards
      const sortedByAqi = [...wardData].sort((a, b) => b.aqi_score - a.aqi_score);
      const sortedByTraffic = [...wardData].sort((a, b) => b.traffic_score - a.traffic_score);
      const sortedByCivic = [...wardData].sort((a, b) => b.civic_score - a.civic_score);
      
      newInsights.push(`Top 3 phường có môi trường tốt nhất: ${sortedByAqi.slice(0, 3).map(w => w.ward.replace('Phường ', '')).join(', ')}`);
      newInsights.push(`Top 3 phường giao thông thông thoáng: ${sortedByTraffic.slice(0, 3).map(w => w.ward.replace('Phường ', '')).join(', ')}`);
      newInsights.push(`Top 3 phường phản hồi dân sự tốt nhất: ${sortedByCivic.slice(0, 3).map(w => w.ward.replace('Phường ', '')).join(', ')}`);
      
      // District analysis
      const districtScores: { [key: string]: number[] } = {};
      wardData.forEach(w => {
        if (!districtScores[w.district]) districtScores[w.district] = [];
        districtScores[w.district].push((w.aqi_score + w.traffic_score + w.civic_score + w.parking_score) / 4);
      });
      
      const bestDistrict = Object.entries(districtScores)
        .map(([d, scores]) => ({ district: d, avg: scores.reduce((a, b) => a + b, 0) / scores.length }))
        .sort((a, b) => b.avg - a.avg)[0];
      
      if (bestDistrict) {
        newInsights.push(`Quận ${bestDistrict.district} có điểm tổng hợp cao nhất: ${bestDistrict.avg.toFixed(1)}/100`);
      }
      newInsights.push('Giờ cao điểm sáng (7-9h) và chiều (17-19h) có lưu lượng giao thông tăng 200-300%.');
      
      setInsights(newInsights);
      
      if (showToast) toast.success('Đã cập nhật dữ liệu phân tích');
    } catch (error) {
      console.error('Error:', error);
      toast.error('Không thể tải dữ liệu');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const exportData = () => {
    const exportPayload = {
      filters: {
        selected_wards: selectedWards.length > 0 ? selectedWards : 'Tất cả 126 phường',
        time_range: timeRange,
        metric_type: metricType,
      },
      correlation: correlationData,
      ward_data: displayWardData,
      all_wards_count: allWardData.length,
      temporal: temporalData,
      insights: insights,
      exported_at: new Date().toISOString(),
    };
    const blob = new Blob([JSON.stringify(exportPayload, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `citylens-insights-${new Date().toISOString().split('T')[0]}.json`;
    link.click();
    toast.success('Đã xuất dữ liệu phân tích');
  };

  // Correlation matrix data
  const correlationMatrix = useMemo(() => {
    const metrics = ['Môi trường', 'Giao thông', 'Dân sự', 'Bãi đỗ xe'];
    const data = displayWardData;
    if (data.length < 2) return [];
    
    const getValue = (item: WardData, metric: string) => {
      switch (metric) {
        case 'Môi trường': return item.aqi_score;
        case 'Giao thông': return item.traffic_score;
        case 'Dân sự': return item.civic_score;
        case 'Bãi đỗ xe': return item.parking_score;
        default: return 0;
      }
    };
    
    // Simplified correlation calculation
    const matrix: { row: string; col: string; value: number }[] = [];
    metrics.forEach((m1, i) => {
      metrics.forEach((m2, j) => {
        if (i === j) {
          matrix.push({ row: m1, col: m2, value: 1.0 });
        } else {
          // Simple correlation based on average difference
          const vals1 = data.map(d => getValue(d, m1));
          const vals2 = data.map(d => getValue(d, m2));
          const avg1 = vals1.reduce((a, b) => a + b, 0) / vals1.length;
          const avg2 = vals2.reduce((a, b) => a + b, 0) / vals2.length;
          
          let cov = 0, std1 = 0, std2 = 0;
          for (let k = 0; k < vals1.length; k++) {
            cov += (vals1[k] - avg1) * (vals2[k] - avg2);
            std1 += (vals1[k] - avg1) ** 2;
            std2 += (vals2[k] - avg2) ** 2;
          }
          const corr = cov / (Math.sqrt(std1) * Math.sqrt(std2)) || 0;
          matrix.push({ row: m1, col: m2, value: Math.round(corr * 100) / 100 });
        }
      });
    });
    return matrix;
  }, [displayWardData]);

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

  return (
    <div className="min-h-screen bg-background p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <BarChart3 className="h-6 w-6 text-green-600 dark:text-green-500" />
            Phân tích Dữ liệu
          </h1>
          <p className="text-muted-foreground text-sm mt-1">
            Phân tích xu hướng và mối tương quan • {allWardData.length} phường
          </p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={exportData}
            className="flex items-center gap-2 px-4 py-2 bg-card border border-border rounded-lg hover:bg-muted transition-colors"
          >
            <Download className="h-4 w-4" />
            Xuất dữ liệu
          </button>
          <button
            onClick={() => fetchData(true)}
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
          maxWards={20}
        />
      </div>

      {/* Tabs */}
      <div className="flex gap-1 p-1 bg-muted rounded-lg w-fit mb-6 flex-wrap">
        <button
          onClick={() => setSelectedTab('correlation')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            selectedTab === 'correlation' ? 'bg-card text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          <TrendingUp className="h-4 w-4 inline mr-2" />
          Tương quan AQI
        </button>
        <button
          onClick={() => setSelectedTab('wards')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            selectedTab === 'wards' ? 'bg-card text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          <MapPin className="h-4 w-4 inline mr-2" />
          {selectedWards.length > 0 ? `So sánh ${selectedWards.length} Phường` : 'So sánh Quận'}
        </button>
        <button
          onClick={() => setSelectedTab('temporal')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            selectedTab === 'temporal' ? 'bg-card text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          <Clock className="h-4 w-4 inline mr-2" />
          Biến động giờ
        </button>
        <button
          onClick={() => setSelectedTab('matrix')}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
            selectedTab === 'matrix' ? 'bg-card text-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          <Grid3X3 className="h-4 w-4 inline mr-2" />
          Ma trận tương quan
        </button>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 gap-6">
        {selectedTab === 'correlation' && (
          <div className="bg-card p-6 rounded-xl border border-border">
            <h3 className="text-lg font-semibold text-foreground mb-4">Tương quan Nhiệt độ và Chỉ số AQI (24 giờ)</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Biểu đồ thể hiện mối quan hệ giữa nhiệt độ và chất lượng không khí. Khi nhiệt độ tăng, 
              các phản ứng quang hóa tạo ra O₃ và PM2.5 làm tăng AQI.
            </p>
            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={correlationData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="hour" tick={{ fontSize: 12 }} />
                <YAxis yAxisId="temp" orientation="left" tick={{ fontSize: 12 }} />
                <YAxis yAxisId="aqi" orientation="right" tick={{ fontSize: 12 }} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
                />
                <Legend />
                <Line 
                  yAxisId="temp"
                  type="monotone" 
                  dataKey="temperature" 
                  stroke="#16a34a" 
                  strokeWidth={2}
                  name="Nhiệt độ (°C)"
                  dot={false}
                />
                <Line 
                  yAxisId="aqi"
                  type="monotone" 
                  dataKey="aqi" 
                  stroke="#2563eb" 
                  strokeWidth={2}
                  name="AQI"
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}

        {selectedTab === 'wards' && (
          <div className="bg-card p-6 rounded-xl border border-border">
            <h3 className="text-lg font-semibold text-foreground mb-4">
              {selectedWards.length > 0 
                ? `So sánh ${selectedWards.length} Phường đã chọn`
                : `So sánh trung bình ${Object.keys(DISTRICTS).length} Quận`}
            </h3>
            <p className="text-sm text-muted-foreground mb-4">
              Điểm số đánh giá trên thang 0-100. Điểm cao hơn cho thấy hiệu suất tốt hơn.
              {selectedWards.length === 0 && ' Chọn phường cụ thể ở bộ lọc để xem chi tiết.'}
            </p>
            <ResponsiveContainer width="100%" height={Math.max(350, displayWardData.length * 35)}>
              <BarChart data={displayWardData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11 }} />
                <YAxis 
                  type="category" 
                  dataKey="ward" 
                  tick={{ fontSize: 11 }} 
                  width={120}
                  tickFormatter={(val) => val.replace('Phường ', 'P. ').replace('Xã ', 'X. ')}
                />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
                />
                <Legend />
                <Bar dataKey="aqi_score" fill="#16a34a" name="Môi trường" />
                <Bar dataKey="traffic_score" fill="#f59e0b" name="Giao thông" />
                <Bar dataKey="civic_score" fill="#2563eb" name="Dân sự" />
                <Bar dataKey="parking_score" fill="#7c3aed" name="Bãi đỗ xe" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}

        {selectedTab === 'temporal' && (
          <div className="bg-card p-6 rounded-xl border border-border">
            <h3 className="text-lg font-semibold text-foreground mb-4">Biến động theo giờ trong ngày</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Lưu lượng giao thông và tỷ lệ đỗ xe thay đổi theo giờ. Giờ cao điểm: 7-9h sáng và 17-19h chiều.
            </p>
            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={temporalData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="hour" tick={{ fontSize: 12 }} />
                <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#fff', border: '1px solid #e5e7eb', borderRadius: '8px' }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="traffic" 
                  stroke="#dc2626" 
                  strokeWidth={2}
                  name="Giao thông (%)"
                  dot={false}
                />
                <Line 
                  type="monotone" 
                  dataKey="parking" 
                  stroke="#7c3aed" 
                  strokeWidth={2}
                  name="Bãi đỗ xe (%)"
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
        
        {selectedTab === 'matrix' && (
          <div className="bg-card p-6 rounded-xl border border-border">
            <h3 className="text-lg font-semibold text-foreground mb-4">Ma trận Tương quan giữa các Chỉ số</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Hệ số tương quan từ -1 (nghịch) đến +1 (thuận). Giá trị gần 0 = không tương quan.
            </p>
            
            {/* Correlation Matrix Grid */}
            <div className="overflow-x-auto">
              <div className="inline-grid gap-1" style={{ gridTemplateColumns: 'auto repeat(4, 100px)' }}>
                {/* Header row */}
                <div></div>
                {['Môi trường', 'Giao thông', 'Dân sự', 'Bãi đỗ xe'].map(col => (
                  <div key={col} className="text-center text-xs font-medium text-muted-foreground p-2">
                    {col}
                  </div>
                ))}
                
                {/* Data rows */}
                {['Môi trường', 'Giao thông', 'Dân sự', 'Bãi đỗ xe'].map(row => (
                  <div key={row} className="contents">
                    <div className="text-xs font-medium text-muted-foreground p-2 text-right">
                      {row}
                    </div>
                    {['Môi trường', 'Giao thông', 'Dân sự', 'Bãi đỗ xe'].map(col => {
                      const cell = correlationMatrix.find(m => m.row === row && m.col === col);
                      const val = cell?.value || 0;
                      const bgColor = val >= 0.7 ? 'bg-green-500' :
                                     val >= 0.3 ? 'bg-green-300' :
                                     val >= -0.3 ? 'bg-gray-200 dark:bg-gray-700' :
                                     val >= -0.7 ? 'bg-red-300' : 'bg-red-500';
                      const textColor = Math.abs(val) >= 0.7 ? 'text-white' : 'text-foreground';
                      
                      return (
                        <div 
                          key={`${row}-${col}`}
                          className={`p-3 text-center text-sm font-medium rounded ${bgColor} ${textColor}`}
                        >
                          {val.toFixed(2)}
                        </div>
                      );
                    })}
                  </div>
                ))}
              </div>
            </div>
            
            {/* Legend */}
            <div className="mt-4 flex items-center gap-4 text-xs text-muted-foreground">
              <span className="flex items-center gap-1">
                <span className="w-4 h-4 rounded bg-green-500"></span>
                Tương quan thuận mạnh
              </span>
              <span className="flex items-center gap-1">
                <span className="w-4 h-4 rounded bg-gray-300 dark:bg-gray-600"></span>
                Không tương quan
              </span>
              <span className="flex items-center gap-1">
                <span className="w-4 h-4 rounded bg-red-500"></span>
                Tương quan nghịch
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Insights */}
      <div className="mt-6 bg-card rounded-xl border border-border p-6">
        <h3 className="text-lg font-semibold text-foreground mb-4">Phát hiện từ dữ liệu ({allWardData.length} phường)</h3>
        <div className="space-y-3">
          {insights.map((insight, i) => (
            <div key={i} className="flex items-start gap-3 p-3 bg-green-50 dark:bg-green-950/30 rounded-lg border border-green-100 dark:border-green-800">
              <div className="w-6 h-6 rounded-full bg-green-600 dark:bg-green-500 text-white flex items-center justify-center text-sm font-medium flex-shrink-0">
                {i + 1}
              </div>
              <p className="text-foreground text-sm">{insight}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
