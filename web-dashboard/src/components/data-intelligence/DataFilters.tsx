// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

'use client';

import { useState, useMemo } from 'react';
import { Search, ChevronDown, X, Check, Calendar, MapPin, Filter } from 'lucide-react';

// 126 phường/xã Hà Nội
export const HANOI_WARDS = [
  // Ba Đình
  "Phường Phúc Xá", "Phường Trúc Bạch", "Phường Vĩnh Phúc", "Phường Cống Vị", 
  "Phường Liễu Giai", "Phường Nguyễn Trung Trực", "Phường Quán Thánh", "Phường Ngọc Hà",
  "Phường Điện Biên", "Phường Đội Cấn", "Phường Ngọc Khánh", "Phường Kim Mã",
  "Phường Giảng Võ", "Phường Thành Công",
  // Hoàn Kiếm
  "Phường Phúc Tân", "Phường Đồng Xuân", "Phường Hàng Mã", "Phường Hàng Buồm",
  "Phường Hàng Đào", "Phường Hàng Bồ", "Phường Cửa Đông", "Phường Lý Thái Tổ",
  "Phường Hàng Bạc", "Phường Hàng Gai", "Phường Chương Dương", "Phường Hàng Trống",
  "Phường Cửa Nam", "Phường Hàng Bông", "Phường Tràng Tiền", "Phường Trần Hưng Đạo",
  "Phường Phan Chu Trinh", "Phường Hàng Bài",
  // Đống Đa
  "Phường Văn Miếu", "Phường Quốc Tử Giám", "Phường Hàng Bột", "Phường Láng Hạ",
  "Phường Láng Thượng", "Phường Ô Chợ Dừa", "Phường Văn Chương", "Phường Cát Linh",
  "Phường Quang Trung", "Phường Khương Thượng", "Phường Ngã Tư Sở", "Phường Khâm Thiên",
  "Phường Trung Phụng", "Phường Trung Liệt", "Phường Phương Liên", "Phường Thịnh Quang",
  "Phường Trung Tự", "Phường Kim Liên", "Phường Phương Mai", "Phường Nam Đồng",
  "Phường Thổ Quan",
  // Hai Bà Trưng  
  "Phường Nguyễn Du", "Phường Bạch Đằng", "Phường Phạm Đình Hổ", "Phường Lê Đại Hành",
  "Phường Đồng Nhân", "Phường Phố Huế", "Phường Đống Mác", "Phường Thanh Lương",
  "Phường Bách Khoa", "Phường Thanh Nhàn", "Phường Cầu Dền", "Phường Bạch Mai",
  "Phường Trương Định", "Phường Đồng Tâm", "Phường Vĩnh Tuy", "Phường Minh Khai",
  "Phường Quỳnh Lôi", "Phường Quỳnh Mai",
  // Cầu Giấy
  "Phường Nghĩa Đô", "Phường Nghĩa Tân", "Phường Mai Dịch", "Phường Dịch Vọng",
  "Phường Dịch Vọng Hậu", "Phường Quan Hoa", "Phường Yên Hòa", "Phường Trung Hòa",
  // Tây Hồ
  "Phường Quảng An", "Phường Nhật Tân", "Phường Tứ Liên", "Phường Phú Thượng",
  "Phường Xuân La", "Phường Thụy Khuê", "Phường Bưởi", "Phường Yên Phụ",
  // Thanh Xuân
  "Phường Thanh Xuân Bắc", "Phường Thanh Xuân Nam", "Phường Thanh Xuân Trung",
  "Phường Khương Đình", "Phường Khương Trung", "Phường Khương Mai", "Phường Hạ Đình",
  "Phường Nhân Chính", "Phường Phương Liệt", "Phường Kim Giang",
  // Long Biên
  "Phường Thượng Thanh", "Phường Ngọc Thụy", "Phường Giang Biên", "Phường Đức Giang",
  "Phường Việt Hưng", "Phường Gia Thụy", "Phường Ngọc Lâm", "Phường Phúc Lợi",
  "Phường Bồ Đề", "Phường Sài Đồng", "Phường Long Biên", "Phường Thạch Bàn",
  "Phường Phúc Đồng", "Phường Cự Khối",
  // Hoàng Mai
  "Phường Mai Động", "Phường Hoàng Văn Thụ", "Phường Giáp Bát", "Phường Lĩnh Nam",
  "Phường Thịnh Liệt", "Phường Trần Phú", "Phường Hoàng Liệt", "Phường Yên Sở",
  "Phường Vĩnh Hưng", "Phường Định Công", "Phường Đại Kim", "Phường Tân Mai",
  "Phường Thanh Trì", "Phường Tương Mai",
  // Nam Từ Liêm
  "Phường Cầu Diễn", "Phường Mỹ Đình 1", "Phường Mỹ Đình 2", "Phường Tây Mỗ",
  "Phường Mễ Trì", "Phường Phú Đô", "Phường Đại Mỗ", "Phường Trung Văn",
  "Phường Phương Canh", "Phường Xuân Phương",
  // Bắc Từ Liêm
  "Phường Thượng Cát", "Phường Liên Mạc", "Phường Đông Ngạc", "Phường Đức Thắng",
  "Phường Thụy Phương", "Phường Tây Tựu", "Phường Xuân Đỉnh", "Phường Xuân Tảo",
  "Phường Minh Khai (Bắc Từ Liêm)", "Phường Cổ Nhuế 1", "Phường Cổ Nhuế 2", "Phường Phú Diễn",
  "Phường Phúc Diễn",
];

// Nhóm phường theo quận
export const DISTRICTS = {
  "Ba Đình": HANOI_WARDS.slice(0, 14),
  "Hoàn Kiếm": HANOI_WARDS.slice(14, 32),
  "Đống Đa": HANOI_WARDS.slice(32, 53),
  "Hai Bà Trưng": HANOI_WARDS.slice(53, 71),
  "Cầu Giấy": HANOI_WARDS.slice(71, 79),
  "Tây Hồ": HANOI_WARDS.slice(79, 87),
  "Thanh Xuân": HANOI_WARDS.slice(87, 97),
  "Long Biên": HANOI_WARDS.slice(97, 111),
  "Hoàng Mai": HANOI_WARDS.slice(111, 125),
  "Nam Từ Liêm": HANOI_WARDS.slice(125, 135) || [],
  "Bắc Từ Liêm": HANOI_WARDS.slice(135) || [],
};

// Time range options
export const TIME_RANGES = [
  { value: 'today', label: 'Hôm nay' },
  { value: '7days', label: '7 ngày qua' },
  { value: '30days', label: '30 ngày qua' },
  { value: '90days', label: '90 ngày qua' },
  { value: 'custom', label: 'Tùy chọn' },
];

// Metric types
export const METRIC_TYPES = [
  { value: 'all', label: 'Tất cả chỉ số' },
  { value: 'environment', label: 'Môi trường' },
  { value: 'traffic', label: 'Giao thông' },
  { value: 'civic', label: 'Phản hồi dân sự' },
  { value: 'parking', label: 'Bãi đỗ xe' },
];

interface DataFiltersProps {
  selectedWards: string[];
  onWardsChange: (wards: string[]) => void;
  timeRange: string;
  onTimeRangeChange: (range: string) => void;
  customDateRange?: { start: string; end: string };
  onCustomDateRangeChange?: (range: { start: string; end: string }) => void;
  metricType: string;
  onMetricTypeChange: (type: string) => void;
  maxWards?: number;
}

export function DataFilters({
  selectedWards,
  onWardsChange,
  timeRange,
  onTimeRangeChange,
  customDateRange,
  onCustomDateRangeChange,
  metricType,
  onMetricTypeChange,
  maxWards = 10,
}: DataFiltersProps) {
  const [isWardDropdownOpen, setIsWardDropdownOpen] = useState(false);
  const [wardSearch, setWardSearch] = useState('');
  const [, setSelectedDistrict] = useState<string | null>(null);

  // Filter wards by search
  const filteredWards = useMemo(() => {
    if (!wardSearch.trim()) return HANOI_WARDS;
    const query = wardSearch.toLowerCase();
    return HANOI_WARDS.filter(ward => ward.toLowerCase().includes(query));
  }, [wardSearch]);

  // Toggle ward selection
  const toggleWard = (ward: string) => {
    if (selectedWards.includes(ward)) {
      onWardsChange(selectedWards.filter(w => w !== ward));
    } else if (selectedWards.length < maxWards) {
      onWardsChange([...selectedWards, ward]);
    }
  };

  // Select all wards in a district
  const selectDistrict = (districtName: string) => {
    const districtWards = DISTRICTS[districtName as keyof typeof DISTRICTS] || [];
    const newWards = [...new Set([...selectedWards, ...districtWards])].slice(0, maxWards);
    onWardsChange(newWards);
    setSelectedDistrict(districtName);
  };

  // Clear all selections
  const clearWards = () => {
    onWardsChange([]);
    setSelectedDistrict(null);
  };

  return (
    <div className="bg-card rounded-xl border border-border p-4 space-y-4">
      <div className="flex items-center gap-2 text-sm font-medium text-foreground">
        <Filter className="h-4 w-4 text-green-600" />
        Bộ lọc dữ liệu
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Ward Selector */}
        <div className="relative">
          <label className="block text-xs font-medium text-muted-foreground mb-1.5">
            <MapPin className="h-3 w-3 inline mr-1" />
            Phường/Xã ({selectedWards.length}/{maxWards})
          </label>
          
          <button
            onClick={() => setIsWardDropdownOpen(!isWardDropdownOpen)}
            className="w-full flex items-center justify-between px-3 py-2 rounded-lg border border-border bg-background text-sm text-foreground hover:bg-muted transition-colors"
          >
            <span className="truncate">
              {selectedWards.length === 0 
                ? 'Tất cả (126 phường)' 
                : selectedWards.length === 1 
                  ? selectedWards[0]
                  : `${selectedWards.length} phường đã chọn`}
            </span>
            <ChevronDown className={`h-4 w-4 transition-transform ${isWardDropdownOpen ? 'rotate-180' : ''}`} />
          </button>

          {/* Dropdown */}
          {isWardDropdownOpen && (
            <div className="absolute z-50 mt-1 w-full bg-card rounded-lg border border-border shadow-lg max-h-80 overflow-hidden">
              {/* Search */}
              <div className="p-2 border-b border-border">
                <div className="relative">
                  <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
                  <input
                    type="text"
                    placeholder="Tìm phường/xã..."
                    value={wardSearch}
                    onChange={(e) => setWardSearch(e.target.value)}
                    className="w-full pl-8 pr-3 py-1.5 text-sm rounded border border-border bg-background focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                </div>
              </div>

              {/* Quick Actions */}
              <div className="p-2 border-b border-border flex gap-2 flex-wrap">
                <button
                  onClick={clearWards}
                  className="px-2 py-1 text-xs rounded bg-muted hover:bg-muted/80 transition-colors"
                >
                  Bỏ chọn tất cả
                </button>
                {Object.keys(DISTRICTS).slice(0, 4).map(district => (
                  <button
                    key={district}
                    onClick={() => selectDistrict(district)}
                    className="px-2 py-1 text-xs rounded bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400 hover:bg-green-200 dark:hover:bg-green-900/50 transition-colors"
                  >
                    {district}
                  </button>
                ))}
              </div>

              {/* Ward List */}
              <div className="max-h-48 overflow-y-auto p-2 space-y-1">
                {filteredWards.map(ward => (
                  <button
                    key={ward}
                    onClick={() => toggleWard(ward)}
                    className={`w-full flex items-center justify-between px-2 py-1.5 rounded text-sm transition-colors ${
                      selectedWards.includes(ward)
                        ? 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400'
                        : 'hover:bg-muted'
                    }`}
                  >
                    <span className="truncate">{ward}</span>
                    {selectedWards.includes(ward) && <Check className="h-4 w-4 flex-shrink-0" />}
                  </button>
                ))}
              </div>

              {/* Close */}
              <div className="p-2 border-t border-border">
                <button
                  onClick={() => setIsWardDropdownOpen(false)}
                  className="w-full py-1.5 text-sm font-medium bg-green-600 text-white rounded hover:bg-green-700 transition-colors"
                >
                  Xong
                </button>
              </div>
            </div>
          )}

          {/* Selected tags */}
          {selectedWards.length > 0 && selectedWards.length <= 3 && (
            <div className="flex flex-wrap gap-1 mt-1.5">
              {selectedWards.map(ward => (
                <span
                  key={ward}
                  className="inline-flex items-center gap-1 px-2 py-0.5 text-xs rounded-full bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400"
                >
                  {ward.replace('Phường ', 'P.').replace('Xã ', 'X.')}
                  <button onClick={() => toggleWard(ward)} className="hover:text-red-600">
                    <X className="h-3 w-3" />
                  </button>
                </span>
              ))}
            </div>
          )}
        </div>

        {/* Time Range */}
        <div>
          <label className="block text-xs font-medium text-muted-foreground mb-1.5">
            <Calendar className="h-3 w-3 inline mr-1" />
            Khoảng thời gian
          </label>
          
          <select
            value={timeRange}
            onChange={(e) => onTimeRangeChange(e.target.value)}
            className="w-full px-3 py-2 rounded-lg border border-border bg-background text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            {TIME_RANGES.map(range => (
              <option key={range.value} value={range.value}>{range.label}</option>
            ))}
          </select>

          {/* Custom Date Range */}
          {timeRange === 'custom' && onCustomDateRangeChange && (
            <div className="flex gap-2 mt-2">
              <input
                type="date"
                value={customDateRange?.start || ''}
                onChange={(e) => onCustomDateRangeChange({ ...customDateRange!, start: e.target.value })}
                className="flex-1 px-2 py-1 text-xs rounded border border-border bg-background"
              />
              <span className="text-muted-foreground self-center">→</span>
              <input
                type="date"
                value={customDateRange?.end || ''}
                onChange={(e) => onCustomDateRangeChange({ ...customDateRange!, end: e.target.value })}
                className="flex-1 px-2 py-1 text-xs rounded border border-border bg-background"
              />
            </div>
          )}
        </div>

        {/* Metric Type */}
        <div>
          <label className="block text-xs font-medium text-muted-foreground mb-1.5">
            Loại chỉ số
          </label>
          
          <select
            value={metricType}
            onChange={(e) => onMetricTypeChange(e.target.value)}
            className="w-full px-3 py-2 rounded-lg border border-border bg-background text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-green-500"
          >
            {METRIC_TYPES.map(type => (
              <option key={type.value} value={type.value}>{type.label}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Active Filters Summary */}
      {(selectedWards.length > 0 || timeRange !== 'today' || metricType !== 'all') && (
        <div className="flex items-center gap-2 pt-2 border-t border-border">
          <span className="text-xs text-muted-foreground">Đang lọc:</span>
          {selectedWards.length > 0 && (
            <span className="px-2 py-0.5 text-xs rounded bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400">
              {selectedWards.length} phường
            </span>
          )}
          {timeRange !== 'today' && (
            <span className="px-2 py-0.5 text-xs rounded bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400">
              {TIME_RANGES.find(r => r.value === timeRange)?.label}
            </span>
          )}
          {metricType !== 'all' && (
            <span className="px-2 py-0.5 text-xs rounded bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-400">
              {METRIC_TYPES.find(t => t.value === metricType)?.label}
            </span>
          )}
          <button
            onClick={() => {
              clearWards();
              onTimeRangeChange('today');
              onMetricTypeChange('all');
            }}
            className="ml-auto text-xs text-muted-foreground hover:text-foreground transition-colors"
          >
            Xóa bộ lọc
          </button>
        </div>
      )}
    </div>
  );
}

// Export Report Modal Component
interface ExportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onExport: (format: string, options: ExportOptions) => void;
  selectedWards: string[];
  timeRange: string;
}

export interface ExportOptions {
  includeSummary: boolean;
  includeDetails: boolean;
  includeCharts: boolean;
  includeRecommendations: boolean;
  includeRawData: boolean;
}

export function ExportModal({ isOpen, onClose, onExport, selectedWards, timeRange }: ExportModalProps) {
  const [format, setFormat] = useState<'pdf' | 'excel' | 'csv' | 'json'>('pdf');
  const [options, setOptions] = useState<ExportOptions>({
    includeSummary: true,
    includeDetails: true,
    includeCharts: true,
    includeRecommendations: true,
    includeRawData: false,
  });

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
      <div className="bg-card rounded-xl border border-border w-full max-w-md">
        <div className="flex items-center justify-between p-4 border-b border-border">
          <h2 className="text-lg font-semibold text-foreground">Xuất báo cáo</h2>
          <button onClick={onClose} className="p-2 hover:bg-muted rounded-lg transition-colors">
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="p-4 space-y-4">
          {/* Report Info */}
          <div className="p-3 bg-muted/50 rounded-lg text-sm">
            <p className="text-muted-foreground">
              <strong>Phạm vi:</strong> {selectedWards.length === 0 ? 'Toàn TP. Hà Nội (126 phường)' : `${selectedWards.length} phường đã chọn`}
            </p>
            <p className="text-muted-foreground">
              <strong>Thời gian:</strong> {TIME_RANGES.find(r => r.value === timeRange)?.label}
            </p>
          </div>

          {/* Format Selection */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">Định dạng</label>
            <div className="grid grid-cols-4 gap-2">
              {(['pdf', 'excel', 'csv', 'json'] as const).map(f => (
                <button
                  key={f}
                  onClick={() => setFormat(f)}
                  className={`py-2 rounded-lg text-sm font-medium transition-colors ${
                    format === f
                      ? 'bg-green-600 text-white'
                      : 'bg-muted hover:bg-muted/80'
                  }`}
                >
                  {f.toUpperCase()}
                </button>
              ))}
            </div>
          </div>

          {/* Content Options */}
          <div>
            <label className="block text-sm font-medium text-foreground mb-2">Nội dung báo cáo</label>
            <div className="space-y-2">
              {[
                { key: 'includeSummary', label: 'Tóm tắt điều hành' },
                { key: 'includeDetails', label: 'Chi tiết theo phường' },
                { key: 'includeCharts', label: 'Biểu đồ xu hướng' },
                { key: 'includeRecommendations', label: 'Khuyến nghị hành động' },
                { key: 'includeRawData', label: 'Dữ liệu raw đầy đủ' },
              ].map(opt => (
                <label key={opt.key} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={options[opt.key as keyof ExportOptions]}
                    onChange={(e) => setOptions({ ...options, [opt.key]: e.target.checked })}
                    className="w-4 h-4 rounded border-border text-green-600 focus:ring-green-500"
                  />
                  <span className="text-sm text-foreground">{opt.label}</span>
                </label>
              ))}
            </div>
          </div>
        </div>

        <div className="flex items-center justify-end gap-2 p-4 border-t border-border">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-border rounded-lg hover:bg-muted transition-colors"
          >
            Hủy
          </button>
          <button
            onClick={() => onExport(format, options)}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            Xuất báo cáo
          </button>
        </div>
      </div>
    </div>
  );
}
