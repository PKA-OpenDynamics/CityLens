/**
 * CityLens Geo Utils - Thư viện xử lý dữ liệu địa lý
 * 
 * Thư viện cung cấp các hàm tiện ích cho việc xử lý dữ liệu địa lý,
 * GeoJSON, và tích hợp với PostGIS trong nền tảng CityLens.
 * 
 * Copyright (C) 2025 CityLens Team
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 */

// ============================================================
// Định nghĩa kiểu GeoJSON
// ============================================================

export type GeoJSONGeometryType = 
  | 'Point' 
  | 'LineString' 
  | 'Polygon' 
  | 'MultiPoint' 
  | 'MultiLineString' 
  | 'MultiPolygon' 
  | 'GeometryCollection';

export interface GeoJSONPoint {
  type: 'Point';
  coordinates: [number, number]; // [longitude, latitude]
}

export interface GeoJSONLineString {
  type: 'LineString';
  coordinates: [number, number][];
}

export interface GeoJSONPolygon {
  type: 'Polygon';
  coordinates: [number, number][][];
}

export interface GeoJSONMultiPoint {
  type: 'MultiPoint';
  coordinates: [number, number][];
}

export interface GeoJSONMultiLineString {
  type: 'MultiLineString';
  coordinates: [number, number][][];
}

export interface GeoJSONMultiPolygon {
  type: 'MultiPolygon';
  coordinates: [number, number][][][];
}

export type GeoJSONGeometry = 
  | GeoJSONPoint 
  | GeoJSONLineString 
  | GeoJSONPolygon 
  | GeoJSONMultiPoint 
  | GeoJSONMultiLineString 
  | GeoJSONMultiPolygon;

export interface GeoJSONFeature<G extends GeoJSONGeometry = GeoJSONGeometry, P = Record<string, unknown>> {
  type: 'Feature';
  geometry: G;
  properties: P;
  id?: string | number;
}

export interface GeoJSONFeatureCollection<G extends GeoJSONGeometry = GeoJSONGeometry, P = Record<string, unknown>> {
  type: 'FeatureCollection';
  features: GeoJSONFeature<G, P>[];
}

// ============================================================
// Tiện ích tạo GeoJSON
// ============================================================

/**
 * Tạo GeoJSON Point từ tọa độ
 * @param lat Vĩ độ
 * @param lon Kinh độ
 * @returns GeoJSON Point object
 */
export function createPoint(lat: number, lon: number): GeoJSONPoint {
  return {
    type: 'Point',
    coordinates: [lon, lat], // GeoJSON dùng [lon, lat]
  };
}

/**
 * Tạo GeoJSON LineString từ danh sách tọa độ
 * @param coordinates Mảng các cặp [lat, lon]
 * @returns GeoJSON LineString object
 */
export function createLineString(coordinates: [number, number][]): GeoJSONLineString {
  return {
    type: 'LineString',
    coordinates: coordinates.map(([lat, lon]) => [lon, lat]),
  };
}

/**
 * Tạo GeoJSON Polygon từ danh sách tọa độ
 * @param coordinates Mảng các cặp [lat, lon] tạo thành vòng khép kín
 * @returns GeoJSON Polygon object
 */
export function createPolygon(coordinates: [number, number][]): GeoJSONPolygon {
  const ring = coordinates.map(([lat, lon]) => [lon, lat] as [number, number]);
  // Đảm bảo vòng khép kín
  if (ring.length > 0 && 
      (ring[0][0] !== ring[ring.length - 1][0] || 
       ring[0][1] !== ring[ring.length - 1][1])) {
    ring.push([...ring[0]] as [number, number]);
  }
  return {
    type: 'Polygon',
    coordinates: [ring],
  };
}

/**
 * Tạo GeoJSON Feature từ geometry và properties
 */
export function createFeature<G extends GeoJSONGeometry, P = Record<string, unknown>>(
  geometry: G,
  properties: P,
  id?: string | number
): GeoJSONFeature<G, P> {
  const feature: GeoJSONFeature<G, P> = {
    type: 'Feature',
    geometry,
    properties,
  };
  if (id !== undefined) {
    feature.id = id;
  }
  return feature;
}

/**
 * Tạo GeoJSON FeatureCollection từ danh sách features
 */
export function createFeatureCollection<G extends GeoJSONGeometry, P = Record<string, unknown>>(
  features: GeoJSONFeature<G, P>[]
): GeoJSONFeatureCollection<G, P> {
  return {
    type: 'FeatureCollection',
    features,
  };
}

// ============================================================
// Tiện ích tính toán địa lý
// ============================================================

const EARTH_RADIUS_KM = 6371;

/**
 * Chuyển đổi độ sang radian
 */
function toRadians(degrees: number): number {
  return degrees * (Math.PI / 180);
}

/**
 * Tính khoảng cách Haversine giữa hai điểm
 * @param point1 GeoJSON Point thứ nhất
 * @param point2 GeoJSON Point thứ hai
 * @returns Khoảng cách tính bằng km
 */
export function distanceBetweenPoints(point1: GeoJSONPoint, point2: GeoJSONPoint): number {
  const [lon1, lat1] = point1.coordinates;
  const [lon2, lat2] = point2.coordinates;
  
  const dLat = toRadians(lat2 - lat1);
  const dLon = toRadians(lon2 - lon1);
  
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRadians(lat1)) *
      Math.cos(toRadians(lat2)) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  
  return EARTH_RADIUS_KM * c;
}

/**
 * Tính tâm điểm (centroid) của một polygon
 * @param polygon GeoJSON Polygon
 * @returns GeoJSON Point tại tâm
 */
export function calculateCentroid(polygon: GeoJSONPolygon): GeoJSONPoint {
  const ring = polygon.coordinates[0];
  let sumLon = 0;
  let sumLat = 0;
  const n = ring.length - 1; // Bỏ điểm cuối (trùng điểm đầu)
  
  for (let i = 0; i < n; i++) {
    sumLon += ring[i][0];
    sumLat += ring[i][1];
  }
  
  return {
    type: 'Point',
    coordinates: [sumLon / n, sumLat / n],
  };
}

/**
 * Tính bounding box của geometry
 * @param geometry GeoJSON Geometry bất kỳ
 * @returns [minLon, minLat, maxLon, maxLat]
 */
export function calculateBoundingBox(geometry: GeoJSONGeometry): [number, number, number, number] {
  let minLon = Infinity;
  let minLat = Infinity;
  let maxLon = -Infinity;
  let maxLat = -Infinity;
  
  function processCoordinate(coord: [number, number]) {
    const [lon, lat] = coord;
    minLon = Math.min(minLon, lon);
    minLat = Math.min(minLat, lat);
    maxLon = Math.max(maxLon, lon);
    maxLat = Math.max(maxLat, lat);
  }
  
  function processCoordinates(coords: unknown) {
    if (Array.isArray(coords)) {
      if (typeof coords[0] === 'number') {
        processCoordinate(coords as [number, number]);
      } else {
        (coords as unknown[]).forEach(c => processCoordinates(c));
      }
    }
  }
  
  processCoordinates(geometry.coordinates);
  
  return [minLon, minLat, maxLon, maxLat];
}

/**
 * Kiểm tra điểm có nằm trong bounding box không
 */
export function isPointInBoundingBox(
  point: GeoJSONPoint,
  bbox: [number, number, number, number]
): boolean {
  const [lon, lat] = point.coordinates;
  const [minLon, minLat, maxLon, maxLat] = bbox;
  return lon >= minLon && lon <= maxLon && lat >= minLat && lat <= maxLat;
}

/**
 * Kiểm tra điểm có nằm trong polygon không (Ray casting algorithm)
 */
export function isPointInPolygon(point: GeoJSONPoint, polygon: GeoJSONPolygon): boolean {
  const [x, y] = point.coordinates;
  const ring = polygon.coordinates[0];
  
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [xi, yi] = ring[i];
    const [xj, yj] = ring[j];
    
    if (((yi > y) !== (yj > y)) && (x < (xj - xi) * (y - yi) / (yj - yi) + xi)) {
      inside = !inside;
    }
  }
  
  return inside;
}

// ============================================================
// Tiện ích chuyển đổi tọa độ
// ============================================================

export interface LatLng {
  lat: number;
  lng: number;
}

/**
 * Chuyển GeoJSON Point sang LatLng object
 */
export function pointToLatLng(point: GeoJSONPoint): LatLng {
  return {
    lat: point.coordinates[1],
    lng: point.coordinates[0],
  };
}

/**
 * Chuyển LatLng object sang GeoJSON Point
 */
export function latLngToPoint(latlng: LatLng): GeoJSONPoint {
  return {
    type: 'Point',
    coordinates: [latlng.lng, latlng.lat],
  };
}

/**
 * Chuyển đổi WKT POINT sang GeoJSON Point
 * @param wkt Chuỗi WKT (VD: "POINT(105.8542 21.0285)")
 */
export function wktPointToGeoJSON(wkt: string): GeoJSONPoint | null {
  const match = wkt.match(/POINT\s*\(\s*([-\d.]+)\s+([-\d.]+)\s*\)/i);
  if (match) {
    return {
      type: 'Point',
      coordinates: [parseFloat(match[1]), parseFloat(match[2])],
    };
  }
  return null;
}

/**
 * Chuyển đổi GeoJSON Point sang WKT
 */
export function geoJSONPointToWkt(point: GeoJSONPoint): string {
  const [lon, lat] = point.coordinates;
  return `POINT(${lon} ${lat})`;
}

// ============================================================
// Hằng số và tiện ích cho Việt Nam / Hà Nội
// ============================================================

/**
 * Bounding box của Hà Nội
 */
export const HANOI_BOUNDING_BOX: [number, number, number, number] = [
  105.28, // minLon
  20.56,  // minLat
  106.02, // maxLon
  21.38,  // maxLat
];

/**
 * Tâm điểm Hà Nội (Hồ Hoàn Kiếm)
 */
export const HANOI_CENTER: GeoJSONPoint = {
  type: 'Point',
  coordinates: [105.8542, 21.0285],
};

/**
 * Kiểm tra điểm có nằm trong khu vực Hà Nội không
 */
export function isInHanoi(point: GeoJSONPoint): boolean {
  return isPointInBoundingBox(point, HANOI_BOUNDING_BOX);
}

// ============================================================
// Export version
// ============================================================

export const VERSION = '1.0.0';
