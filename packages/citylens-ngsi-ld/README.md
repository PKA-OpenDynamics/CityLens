# CityLens NGSI-LD

Thư viện xây dựng và xử lý NGSI-LD entities theo chuẩn ETSI cho nền tảng CityLens Smart City.

## Cài đặt

```bash
npm install @pka_opendynamics_2025/citylens-ngsi-ld
```

## Sử dụng

### Tạo Entity ID

```typescript
import { createEntityId, parseEntityId, isValidEntityId } from '@pka_opendynamics_2025/citylens-ngsi-ld';

// Tạo URN theo chuẩn NGSI-LD
const id = createEntityId('CivicIssue', '12345');
// => 'urn:ngsi-ld:CivicIssue:12345'

// Phân tích URN
const parsed = parseEntityId(id);
// => { entityType: 'CivicIssue', id: '12345' }

// Kiểm tra URN hợp lệ
console.log(isValidEntityId(id)); // => true
```

### Tạo Properties

```typescript
import { createProperty, createGeoProperty, createRelationship } from '@pka_opendynamics_2025/citylens-ngsi-ld';

// Property đơn giản
const name = createProperty('Hà Nội');

// Property với thời gian quan sát
const temperature = createProperty(28.5, {
  observedAt: new Date(),
  unitCode: 'CEL',
});

// GeoProperty (vị trí)
const location = createGeoProperty(21.0285, 105.8542);

// Relationship (liên kết)
const refUser = createRelationship('urn:ngsi-ld:User:admin');
```

### Tạo Smart City Entities

```typescript
import {
  createAirQualityObserved,
  createTrafficFlowObserved,
  createCivicIssue,
} from '@pka_opendynamics_2025/citylens-ngsi-ld';

// Tạo AirQualityObserved entity
const airQuality = createAirQualityObserved({
  id: 'station-001',
  location: { lat: 21.0285, lon: 105.8542 },
  aqi: 75,
  pm25: 45.2,
  pm10: 68.1,
  source: 'AQICN',
});

// Tạo TrafficFlowObserved entity
const traffic = createTrafficFlowObserved({
  id: 'road-001',
  location: { lat: 21.0285, lon: 105.8542 },
  intensity: 450,
  averageSpeed: 35,
  congestionLevel: 'moderate',
});

// Tạo CivicIssue entity (báo cáo công dân)
const issue = createCivicIssue({
  id: 'report-001',
  title: 'Đèn đường hỏng',
  description: 'Đèn đường tại ngã tư không hoạt động',
  location: { lat: 21.0285, lon: 105.8542 },
  category: 'infrastructure',
  priority: 'high',
  reportedBy: 'user123',
});
```

### Validate Entity

```typescript
import { validateEntity } from '@pka_opendynamics_2025/citylens-ngsi-ld';

const result = validateEntity(entity);
if (!result.valid) {
  console.error('Lỗi:', result.errors);
}
```

### Xây dựng Query

```typescript
import { buildQueryString } from '@pka_opendynamics_2025/citylens-ngsi-ld';

const query = buildQueryString({
  type: 'AirQualityObserved',
  geoQ: {
    geometry: 'Point',
    coordinates: [105.8542, 21.0285],
    georel: 'near',
    maxDistance: 5000, // 5km
  },
  limit: 10,
});
// => "type=AirQualityObserved&geometry=Point&coordinates=[105.8542,21.0285]&georel=near;maxDistance==5000&limit=10"
```

## API

### Entity ID

- `createEntityId(entityType, id)` - Tạo URN chuẩn NGSI-LD
- `parseEntityId(urn)` - Phân tích URN
- `isValidEntityId(urn)` - Kiểm tra URN hợp lệ

### Property Builders

- `createProperty(value, options?)` - Tạo Property
- `createGeoProperty(lat, lon)` - Tạo GeoProperty
- `createRelationship(targetId)` - Tạo Relationship

### Entity Builders

- `createAirQualityObserved(input)` - Tạo AirQualityObserved
- `createTrafficFlowObserved(input)` - Tạo TrafficFlowObserved
- `createCivicIssue(input)` - Tạo CivicIssue

### Validation & Query

- `validateEntity(entity)` - Kiểm tra entity hợp lệ
- `buildQueryString(params)` - Xây dựng query string

### Constants

- `NGSI_LD_CORE_CONTEXT` - ETSI Core Context URL
- `SMART_DATA_MODELS_CONTEXT` - Smart Data Models Context URL
- `CITYLENS_CONTEXT` - CityLens Context URL
- `DEFAULT_CONTEXTS` - Mảng contexts mặc định

## Kiểu dữ liệu

```typescript
interface NgsiLdProperty<T> {
  type: 'Property';
  value: T;
  observedAt?: string;
  unitCode?: string;
}

interface NgsiLdGeoProperty {
  type: 'GeoProperty';
  value: { type: 'Point'; coordinates: [number, number] };
}

interface NgsiLdRelationship {
  type: 'Relationship';
  object: string;
}

interface NgsiLdEntity {
  '@context'?: string | string[];
  id: string;
  type: string;
  [key: string]: unknown;
}
```

## Tham khảo

- [ETSI NGSI-LD Specification](https://www.etsi.org/deliver/etsi_gs/CIM/001_099/009/01.06.01_60/gs_CIM009v010601p.pdf)
- [Smart Data Models](https://smartdatamodels.org/)
- [FIWARE Data Models](https://fiware-datamodels.readthedocs.io/)

## Giấy phép

GPL-3.0
