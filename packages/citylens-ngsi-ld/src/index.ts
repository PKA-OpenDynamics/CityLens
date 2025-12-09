// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)
/**
 * CityLens NGSI-LD - Thư viện xây dựng và xử lý NGSI-LD entities
 * 
 * Thư viện cung cấp các công cụ để xây dựng NGSI-LD entities theo chuẩn ETSI,
 * hỗ trợ các data models cho Smart City như AirQualityObserved, TrafficFlowObserved,
 * và CivicIssue.
 * 
 * Copyright (C) 2025 CityLens Team
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 */

// ============================================================
// NGSI-LD Context và Constants
// ============================================================

/**
 * NGSI-LD Core Context URL
 */
export const NGSI_LD_CORE_CONTEXT = 'https://uri.etsi.org/ngsi-ld/v1/ngsi-ld-core-context.jsonld';

/**
 * Smart Data Models Context URL
 */
export const SMART_DATA_MODELS_CONTEXT = 'https://smartdatamodels.org/context.jsonld';

/**
 * CityLens Custom Context
 */
export const CITYLENS_CONTEXT = 'https://citylens.io/context/v1/citylens.jsonld';

/**
 * Default contexts cho CityLens entities
 */
export const DEFAULT_CONTEXTS = [
  NGSI_LD_CORE_CONTEXT,
  SMART_DATA_MODELS_CONTEXT,
  CITYLENS_CONTEXT,
];

// ============================================================
// Định nghĩa kiểu NGSI-LD
// ============================================================

export interface NgsiLdProperty<T> {
  type: 'Property';
  value: T;
  observedAt?: string;
  unitCode?: string;
}

export interface NgsiLdGeoProperty {
  type: 'GeoProperty';
  value: {
    type: 'Point';
    coordinates: [number, number];
  };
}

export interface NgsiLdRelationship {
  type: 'Relationship';
  object: string;
}

export interface NgsiLdTemporalProperty<T> {
  type: 'Property';
  value: T;
  observedAt: string;
}

export interface NgsiLdEntity {
  '@context'?: string | string[];
  id: string;
  type: string;
  [key: string]: unknown;
}

// ============================================================
// Entity ID Helpers
// ============================================================

/**
 * Tạo NGSI-LD Entity URN
 * @param entityType Loại entity (VD: AirQualityObserved, CivicIssue)
 * @param id ID duy nhất
 * @returns URN theo chuẩn NGSI-LD
 */
export function createEntityId(entityType: string, id: string | number): string {
  return `urn:ngsi-ld:${entityType}:${id}`;
}

/**
 * Phân tích NGSI-LD Entity URN
 * @param urn URN đầy đủ
 * @returns Object chứa entityType và id, hoặc null nếu không hợp lệ
 */
export function parseEntityId(urn: string): { entityType: string; id: string } | null {
  const pattern = /^urn:ngsi-ld:([^:]+):(.+)$/;
  const match = urn.match(pattern);
  if (match) {
    return { entityType: match[1], id: match[2] };
  }
  return null;
}

/**
 * Kiểm tra URN có đúng chuẩn NGSI-LD không
 */
export function isValidEntityId(urn: string): boolean {
  return /^urn:ngsi-ld:[^:]+:.+$/.test(urn);
}

// ============================================================
// Property Builders
// ============================================================

/**
 * Tạo NGSI-LD Property
 */
export function createProperty<T>(
  value: T,
  options?: { observedAt?: string | Date; unitCode?: string }
): NgsiLdProperty<T> {
  const prop: NgsiLdProperty<T> = {
    type: 'Property',
    value,
  };
  if (options?.observedAt) {
    prop.observedAt = options.observedAt instanceof Date 
      ? options.observedAt.toISOString() 
      : options.observedAt;
  }
  if (options?.unitCode) {
    prop.unitCode = options.unitCode;
  }
  return prop;
}

/**
 * Tạo NGSI-LD GeoProperty (Point)
 * @param lat Vĩ độ
 * @param lon Kinh độ
 */
export function createGeoProperty(lat: number, lon: number): NgsiLdGeoProperty {
  return {
    type: 'GeoProperty',
    value: {
      type: 'Point',
      coordinates: [lon, lat], // GeoJSON format: [longitude, latitude]
    },
  };
}

/**
 * Tạo NGSI-LD Relationship
 * @param targetId URN của entity đích
 */
export function createRelationship(targetId: string): NgsiLdRelationship {
  return {
    type: 'Relationship',
    object: targetId,
  };
}

// ============================================================
// Smart City Entity Builders
// ============================================================

export interface AirQualityObservedInput {
  id: string | number;
  location: { lat: number; lon: number };
  aqi: number;
  pm25?: number;
  pm10?: number;
  no2?: number;
  so2?: number;
  co?: number;
  o3?: number;
  observedAt?: Date | string;
  source?: string;
}

/**
 * Tạo AirQualityObserved entity theo Smart Data Models
 */
export function createAirQualityObserved(input: AirQualityObservedInput): NgsiLdEntity {
  const observedAt = input.observedAt 
    ? (input.observedAt instanceof Date ? input.observedAt.toISOString() : input.observedAt)
    : new Date().toISOString();

  const entity: NgsiLdEntity = {
    '@context': DEFAULT_CONTEXTS,
    id: createEntityId('AirQualityObserved', input.id),
    type: 'AirQualityObserved',
    location: createGeoProperty(input.location.lat, input.location.lon),
    airQualityIndex: createProperty(input.aqi, { observedAt }),
    dateObserved: createProperty(observedAt),
  };

  if (input.pm25 !== undefined) {
    entity.pm25 = createProperty(input.pm25, { observedAt, unitCode: 'GQ' }); // µg/m³
  }
  if (input.pm10 !== undefined) {
    entity.pm10 = createProperty(input.pm10, { observedAt, unitCode: 'GQ' });
  }
  if (input.no2 !== undefined) {
    entity.no2 = createProperty(input.no2, { observedAt, unitCode: 'GQ' });
  }
  if (input.so2 !== undefined) {
    entity.so2 = createProperty(input.so2, { observedAt, unitCode: 'GQ' });
  }
  if (input.co !== undefined) {
    entity.co = createProperty(input.co, { observedAt, unitCode: 'GQ' });
  }
  if (input.o3 !== undefined) {
    entity.o3 = createProperty(input.o3, { observedAt, unitCode: 'GQ' });
  }
  if (input.source) {
    entity.source = createProperty(input.source);
  }

  return entity;
}

export interface TrafficFlowObservedInput {
  id: string | number;
  location: { lat: number; lon: number };
  intensity: number;
  averageSpeed?: number;
  congestionLevel?: 'free' | 'light' | 'moderate' | 'heavy' | 'severe';
  laneId?: string;
  observedAt?: Date | string;
}

/**
 * Tạo TrafficFlowObserved entity theo Smart Data Models
 */
export function createTrafficFlowObserved(input: TrafficFlowObservedInput): NgsiLdEntity {
  const observedAt = input.observedAt 
    ? (input.observedAt instanceof Date ? input.observedAt.toISOString() : input.observedAt)
    : new Date().toISOString();

  const entity: NgsiLdEntity = {
    '@context': DEFAULT_CONTEXTS,
    id: createEntityId('TrafficFlowObserved', input.id),
    type: 'TrafficFlowObserved',
    location: createGeoProperty(input.location.lat, input.location.lon),
    intensity: createProperty(input.intensity, { observedAt }),
    dateObserved: createProperty(observedAt),
  };

  if (input.averageSpeed !== undefined) {
    entity.averageSpeed = createProperty(input.averageSpeed, { observedAt, unitCode: 'KMH' });
  }
  if (input.congestionLevel) {
    entity.congestionLevel = createProperty(input.congestionLevel, { observedAt });
  }
  if (input.laneId) {
    entity.laneId = createProperty(input.laneId);
  }

  return entity;
}

export interface CivicIssueInput {
  id: string | number;
  title: string;
  description: string;
  location: { lat: number; lon: number };
  category: string;
  status?: 'pending' | 'in_progress' | 'resolved' | 'rejected';
  priority?: 'low' | 'medium' | 'high' | 'critical';
  reportedBy?: string;
  assignedTo?: string;
  createdAt?: Date | string;
  imageUrl?: string;
}

/**
 * Tạo CivicIssue entity (CityLens custom model)
 */
export function createCivicIssue(input: CivicIssueInput): NgsiLdEntity {
  const createdAt = input.createdAt 
    ? (input.createdAt instanceof Date ? input.createdAt.toISOString() : input.createdAt)
    : new Date().toISOString();

  const entity: NgsiLdEntity = {
    '@context': DEFAULT_CONTEXTS,
    id: createEntityId('CivicIssue', input.id),
    type: 'CivicIssue',
    title: createProperty(input.title),
    description: createProperty(input.description),
    location: createGeoProperty(input.location.lat, input.location.lon),
    category: createProperty(input.category),
    status: createProperty(input.status || 'pending'),
    priority: createProperty(input.priority || 'medium'),
    dateCreated: createProperty(createdAt),
  };

  if (input.reportedBy) {
    entity.reportedBy = createRelationship(createEntityId('User', input.reportedBy));
  }
  if (input.assignedTo) {
    entity.assignedTo = createRelationship(createEntityId('User', input.assignedTo));
  }
  if (input.imageUrl) {
    entity.image = createProperty(input.imageUrl);
  }

  return entity;
}

// ============================================================
// Entity Validation
// ============================================================

export interface ValidationResult {
  valid: boolean;
  errors: string[];
}

/**
 * Kiểm tra NGSI-LD entity có hợp lệ không
 */
export function validateEntity(entity: unknown): ValidationResult {
  const errors: string[] = [];
  
  if (!entity || typeof entity !== 'object') {
    return { valid: false, errors: ['Entity must be an object'] };
  }
  
  const e = entity as Record<string, unknown>;
  
  if (!e.id) {
    errors.push('Missing required field: id');
  } else if (typeof e.id !== 'string' || !isValidEntityId(e.id)) {
    errors.push('Invalid entity id format. Must be urn:ngsi-ld:{Type}:{id}');
  }
  
  if (!e.type) {
    errors.push('Missing required field: type');
  } else if (typeof e.type !== 'string') {
    errors.push('Field "type" must be a string');
  }
  
  return {
    valid: errors.length === 0,
    errors,
  };
}

// ============================================================
// NGSI-LD Query Helpers
// ============================================================

export interface NgsiLdQueryParams {
  type?: string;
  q?: string;
  geoQ?: {
    geometry: 'Point';
    coordinates: [number, number];
    georel: 'near' | 'within' | 'contains' | 'intersects';
    maxDistance?: number;
  };
  limit?: number;
  offset?: number;
}

/**
 * Xây dựng query string cho NGSI-LD API
 */
export function buildQueryString(params: NgsiLdQueryParams): string {
  const queryParts: string[] = [];
  
  if (params.type) {
    queryParts.push(`type=${encodeURIComponent(params.type)}`);
  }
  
  if (params.q) {
    queryParts.push(`q=${encodeURIComponent(params.q)}`);
  }
  
  if (params.geoQ) {
    const { geometry, coordinates, georel, maxDistance } = params.geoQ;
    let georelValue: string = georel;
    if (maxDistance !== undefined) {
      georelValue = `${georel};maxDistance==${maxDistance}`;
    }
    queryParts.push(`geometry=${geometry}`);
    queryParts.push(`coordinates=${JSON.stringify(coordinates)}`);
    queryParts.push(`georel=${georelValue}`);
  }
  
  if (params.limit !== undefined) {
    queryParts.push(`limit=${params.limit}`);
  }
  
  if (params.offset !== undefined) {
    queryParts.push(`offset=${params.offset}`);
  }
  
  return queryParts.join('&');
}

// ============================================================
// Export version
// ============================================================

export const VERSION = '1.0.0';
