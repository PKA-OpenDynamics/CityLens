# CityLens Utils

Thư viện tiện ích cho nền tảng CityLens Smart City.

## Cài đặt

```bash
npm install @pka_opendynamics_2025/citylens-utils
```

## Sử dụng

```typescript
import {
  calculateDistance,
  createNgsiLdId,
  getAqiInfo,
  formatDateVi,
  ReportStatus,
  getReportStatusInfo,
} from '@pka_opendynamics_2025/citylens-utils';

// Tính khoảng cách giữa 2 điểm
const distance = calculateDistance(21.0285, 105.8542, 21.0378, 105.8342);
console.log(`Khoảng cách: ${distance.toFixed(2)} km`);

// Tạo NGSI-LD Entity ID
const entityId = createNgsiLdId('CivicIssue', '12345');
// => 'urn:ngsi-ld:CivicIssue:12345'

// Lấy thông tin AQI
const aqiInfo = getAqiInfo(75);
console.log(aqiInfo.labelVi); // => 'Trung bình'

// Format ngày tháng tiếng Việt
const dateStr = formatDateVi(new Date());
console.log(dateStr); // => '24/01/2025 21:30'

// Lấy thông tin trạng thái báo cáo
const statusInfo = getReportStatusInfo(ReportStatus.IN_PROGRESS);
console.log(statusInfo.labelVi); // => 'Đang xử lý'
```

## API

### Tiện ích tọa độ địa lý

- `calculateDistance(lat1, lon1, lat2, lon2)` - Tính khoảng cách (km)
- `toRadians(degrees)` - Chuyển độ sang radian
- `toDegrees(radians)` - Chuyển radian sang độ
- `isValidCoordinate(lat, lon)` - Kiểm tra tọa độ hợp lệ

### Tiện ích NGSI-LD

- `createNgsiLdId(entityType, id)` - Tạo URN chuẩn NGSI-LD
- `parseNgsiLdId(urn)` - Phân tích URN
- `isValidNgsiLdUrn(urn)` - Kiểm tra URN hợp lệ

### Tiện ích AQI

- `getAqiInfo(aqi)` - Lấy thông tin mức độ AQI
- `AqiLevel` - Enum các mức độ AQI

### Tiện ích format

- `formatNumberVi(num)` - Format số theo chuẩn Việt Nam
- `formatDateVi(date)` - Format ngày tháng tiếng Việt
- `formatDistance(km)` - Format khoảng cách thân thiện

### Tiện ích báo cáo

- `getReportStatusInfo(status)` - Lấy thông tin trạng thái
- `ReportStatus` - Enum trạng thái báo cáo

## Giấy phép

GPL-3.0
