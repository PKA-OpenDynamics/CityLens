# CityLens Geo Utils

Thư viện xử lý dữ liệu địa lý và GeoJSON cho nền tảng CityLens Smart City.

## Cài đặt

```bash
npm install @pka_opendynamics_2025/citylens-geo-utils
```

## Sử dụng

```typescript
import {
  createPoint,
  createPolygon,
  createFeature,
  distanceBetweenPoints,
  calculateCentroid,
  isPointInPolygon,
  wktPointToGeoJSON,
  HANOI_CENTER,
  isInHanoi,
} from '@pka_opendynamics_2025/citylens-geo-utils';

// Tạo GeoJSON Point
const point = createPoint(21.0285, 105.8542);

// Tính khoảng cách giữa 2 điểm
const point1 = createPoint(21.0285, 105.8542);
const point2 = createPoint(21.0378, 105.8342);
const distance = distanceBetweenPoints(point1, point2);
console.log(`Khoảng cách: ${distance.toFixed(2)} km`);

// Tạo Feature với properties
const feature = createFeature(point, {
  name: 'Hồ Hoàn Kiếm',
  type: 'lake',
});

// Chuyển đổi WKT sang GeoJSON
const geoPoint = wktPointToGeoJSON('POINT(105.8542 21.0285)');

// Kiểm tra điểm trong khu vực Hà Nội
console.log(isInHanoi(HANOI_CENTER)); // => true

// Tạo Polygon và kiểm tra điểm trong polygon
const polygon = createPolygon([
  [21.03, 105.85],
  [21.03, 105.86],
  [21.02, 105.86],
  [21.02, 105.85],
]);
console.log(isPointInPolygon(point, polygon)); // => true/false
```

## API

### Tạo GeoJSON

- `createPoint(lat, lon)` - Tạo GeoJSON Point
- `createLineString(coordinates)` - Tạo GeoJSON LineString
- `createPolygon(coordinates)` - Tạo GeoJSON Polygon
- `createFeature(geometry, properties, id?)` - Tạo GeoJSON Feature
- `createFeatureCollection(features)` - Tạo GeoJSON FeatureCollection

### Tính toán địa lý

- `distanceBetweenPoints(point1, point2)` - Khoảng cách Haversine (km)
- `calculateCentroid(polygon)` - Tính tâm điểm polygon
- `calculateBoundingBox(geometry)` - Tính bounding box
- `isPointInBoundingBox(point, bbox)` - Kiểm tra điểm trong bbox
- `isPointInPolygon(point, polygon)` - Kiểm tra điểm trong polygon

### Chuyển đổi tọa độ

- `pointToLatLng(point)` - GeoJSON Point sang {lat, lng}
- `latLngToPoint(latlng)` - {lat, lng} sang GeoJSON Point
- `wktPointToGeoJSON(wkt)` - WKT POINT sang GeoJSON
- `geoJSONPointToWkt(point)` - GeoJSON Point sang WKT

### Hằng số Hà Nội

- `HANOI_BOUNDING_BOX` - Bounding box khu vực Hà Nội
- `HANOI_CENTER` - Tâm điểm Hà Nội (Hồ Hoàn Kiếm)
- `isInHanoi(point)` - Kiểm tra điểm trong Hà Nội

## Kiểu dữ liệu

```typescript
interface GeoJSONPoint {
  type: 'Point';
  coordinates: [number, number]; // [longitude, latitude]
}

interface GeoJSONFeature<G, P> {
  type: 'Feature';
  geometry: G;
  properties: P;
  id?: string | number;
}

interface LatLng {
  lat: number;
  lng: number;
}
```

## Giấy phép

GPL-3.0
