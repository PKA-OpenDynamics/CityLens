// Generate sample map data for CityLens

interface MapMarker {
  id: string;
  type: 'report' | 'sensor' | 'facility';
  coordinates: [number, number];
  title: string;
  description?: string;
  severity?: 'low' | 'medium' | 'high';
}

// Hanoi bounds
const HANOI_BOUNDS = {
  north: 21.15,
  south: 20.95,
  east: 105.95,
  west: 105.75,
};

// Random coordinate within Hanoi
const randomCoordinate = (): [number, number] => {
  const lat = HANOI_BOUNDS.south + Math.random() * (HANOI_BOUNDS.north - HANOI_BOUNDS.south);
  const lng = HANOI_BOUNDS.west + Math.random() * (HANOI_BOUNDS.east - HANOI_BOUNDS.west);
  return [lat, lng];
};

// Report templates
const REPORT_TEMPLATES = [
  { title: 'Đường ngập nước', description: 'Đường bị ngập sau mưa lớn', severities: ['high', 'medium'] },
  { title: 'Ổ gà trên đường', description: 'Nhiều ổ gà cần sửa chữa', severities: ['medium', 'low'] },
  { title: 'Rác thải tồn đọng', description: 'Rác chưa được thu gom', severities: ['medium', 'low'] },
  { title: 'Đèn giao thông hỏng', description: 'Đèn tín hiệu không hoạt động', severities: ['high'] },
  { title: 'Cây đổ chắn đường', description: 'Cây bị đổ chắn lối đi', severities: ['high', 'medium'] },
  { title: 'Cống thoát nước tắc', description: 'Nước không thoát được', severities: ['medium'] },
  { title: 'Vỉa hè hư hỏng', description: 'Vỉa hè bị sụt lún', severities: ['low'] },
  { title: 'Biển báo mất', description: 'Biển báo giao thông bị mất', severities: ['low'] },
  { title: 'Cột điện nghiêng', description: 'Cột điện có nguy cơ ngã', severities: ['high'] },
  { title: 'Nước thải tràn', description: 'Nước thải tràn ra đường', severities: ['high'] },
];

// Sensor templates
const SENSOR_TEMPLATES = [
  { title: 'Cảm biến AQI', values: ['PM2.5: 35 μg/m³', 'PM10: 62 μg/m³', 'AQI: 89'] },
  { title: 'Cảm biến nhiệt độ', values: ['Nhiệt độ: 32°C', 'Nhiệt độ: 28°C', 'Nhiệt độ: 35°C'] },
  { title: 'Cảm biến độ ẩm', values: ['Độ ẩm: 78%', 'Độ ẩm: 65%', 'Độ ẩm: 82%'] },
  { title: 'Cảm biến giao thông', values: ['Tốc độ TB: 25 km/h', 'Lưu lượng: Cao', 'Ùn tắc: Trung bình'] },
  { title: 'Cảm biến tiếng ồn', values: ['75 dB', '68 dB', '82 dB'] },
  { title: 'Cảm biến ánh sáng', values: ['Độ sáng: 850 lux', 'Độ sáng: 1200 lux', 'Độ sáng: 650 lux'] },
];

// Facility templates
const FACILITY_TEMPLATES = [
  { type: 'Bệnh viện', names: ['Bệnh viện Chợ Rẫy', 'Bệnh viện 115', 'Bệnh viện Từ Dũ', 'BV Nhi Đồng 1'] },
  { type: 'Công viên', names: ['Công viên Gia Định', 'Công viên Tao Đàn', 'Công viên 23/9', 'CV Lê Văn Tám'] },
  { type: 'Trường học', names: ['Trường THPT Lê Hồng Phong', 'Trường ĐH Bách Khoa', 'Trường THPT Trần Đại Nghĩa'] },
  { type: 'Chợ', names: ['Chợ Bến Thành', 'Chợ Bình Tây', 'Chợ An Đông', 'Chợ Tân Định'] },
  { type: 'Trạm xe buýt', names: ['Trạm Bến xe Miền Đông', 'Trạm Chợ Lớn', 'Trạm Quận 1'] },
];

// Generate reports
export const generateReports = (count: number = 50): MapMarker[] => {
  const reports: MapMarker[] = [];
  
  for (let i = 0; i < count; i++) {
    const template = REPORT_TEMPLATES[Math.floor(Math.random() * REPORT_TEMPLATES.length)];
    const severity = template.severities[Math.floor(Math.random() * template.severities.length)] as 'low' | 'medium' | 'high';
    
    reports.push({
      id: `report-${i}`,
      type: 'report',
      coordinates: randomCoordinate(),
      title: template.title,
      description: template.description,
      severity,
    });
  }
  
  return reports;
};

// Generate sensors
export const generateSensors = (count: number = 100): MapMarker[] => {
  const sensors: MapMarker[] = [];
  
  for (let i = 0; i < count; i++) {
    const template = SENSOR_TEMPLATES[Math.floor(Math.random() * SENSOR_TEMPLATES.length)];
    const value = template.values[Math.floor(Math.random() * template.values.length)];
    
    sensors.push({
      id: `sensor-${i}`,
      type: 'sensor',
      coordinates: randomCoordinate(),
      title: template.title,
      description: value,
    });
  }
  
  return sensors;
};

// Generate facilities
export const generateFacilities = (count: number = 30): MapMarker[] => {
  const facilities: MapMarker[] = [];
  
  for (let i = 0; i < count; i++) {
    const template = FACILITY_TEMPLATES[Math.floor(Math.random() * FACILITY_TEMPLATES.length)];
    const name = template.names[Math.floor(Math.random() * template.names.length)];
    
    facilities.push({
      id: `facility-${i}`,
      type: 'facility',
      coordinates: randomCoordinate(),
      title: name,
      description: template.type,
    });
  }
  
  return facilities;
};

// Generate all markers
export const generateAllMarkers = (
  reportCount: number = 50,
  sensorCount: number = 100,
  facilityCount: number = 30
): MapMarker[] => {
  return [
    ...generateReports(reportCount),
    ...generateSensors(sensorCount),
    ...generateFacilities(facilityCount),
  ];
};

// Get markers by severity
export const getMarkersBySeverity = (markers: MapMarker[], severity: 'low' | 'medium' | 'high'): MapMarker[] => {
  return markers.filter(m => m.severity === severity);
};

// Get markers by type
export const getMarkersByType = (markers: MapMarker[], type: 'report' | 'sensor' | 'facility'): MapMarker[] => {
  return markers.filter(m => m.type === type);
};

// Get markers in area (simple bounding box)
export const getMarkersInArea = (
  markers: MapMarker[],
  bounds: { north: number; south: number; east: number; west: number }
): MapMarker[] => {
  return markers.filter(m => {
    const [lat, lng] = m.coordinates;
    return lat >= bounds.south && lat <= bounds.north && lng >= bounds.west && lng <= bounds.east;
  });
};

// Calculate marker statistics
export const getMarkerStats = (markers: MapMarker[]) => {
  const stats = {
    total: markers.length,
    reports: markers.filter(m => m.type === 'report').length,
    sensors: markers.filter(m => m.type === 'sensor').length,
    facilities: markers.filter(m => m.type === 'facility').length,
    highSeverity: markers.filter(m => m.severity === 'high').length,
    mediumSeverity: markers.filter(m => m.severity === 'medium').length,
    lowSeverity: markers.filter(m => m.severity === 'low').length,
  };
  
  return stats;
};

