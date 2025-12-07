// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

/**
 * CityLens API Services
 * Connects web dashboard to backend REST API
 */

import { apiClient } from './api-client';

// ============================================
// Types
// ============================================

export interface ReportStatistics {
  total: number;
  pending: number;
  in_progress: number;
  resolved: number;
  verified: number;
  today: number;
  this_week: number;
  resolution_rate: number;
}

export interface Report {
  id: number;
  user_id: number;
  category: string;
  subcategory: string | null;
  title: string;
  description: string;
  address: string | null;
  district_id: number | null;
  latitude: number;
  longitude: number;
  status: 'pending' | 'verified' | 'in_progress' | 'resolved' | 'rejected';
  priority: 'low' | 'normal' | 'high' | 'urgent';
  created_at: string;
  updated_at: string | null;
}

export interface ReportListResponse {
  reports: Report[];
  total: number;
  skip: number;
  limit: number;
}

export interface NearbyReport {
  id: number;
  title: string;
  category: string;
  status: string;
  latitude: number;
  longitude: number;
  distance_meters: number;
  created_at: string;
}

export interface NearbyReportsResponse {
  center: { latitude: number; longitude: number };
  radius_meters: number;
  reports: NearbyReport[];
  total: number;
}

export interface Facility {
  id: number;
  osm_id: number | null;
  name: string;
  name_en: string | null;
  category: string;
  subcategory: string | null;
  address: string | null;
  district_id: number | null;
  latitude: number;
  longitude: number;
  phone: string | null;
  website: string | null;
  opening_hours: string | null;
  capacity: number | null;
  rating: number | null;
  source: string | null;
  created_at: string;
}

export interface FacilityListResponse {
  facilities: Facility[];
  total: number;
  page: number;
  limit: number;
}

export interface NearbyFacility {
  id: number;
  name: string;
  category: string;
  subcategory: string | null;
  address: string | null;
  latitude: number;
  longitude: number;
  distance_meters: number;
  phone: string | null;
  opening_hours: string | null;
  rating: number | null;
}

export interface NearbyFacilitiesResponse {
  center_lat: number;
  center_lng: number;
  radius_meters: number;
  facilities: NearbyFacility[];
  total: number;
}

export interface Boundary {
  id: number;
  osm_id: number | null;
  name: string;
  name_en: string | null;
  admin_level: number;
  parent_id: number | null;
  population: number | null;
  area_km2: number | null;
  created_at: string | null;
}

export interface BoundaryListResponse {
  boundaries: Boundary[];
  total: number;
}

// Boundary simple item for dropdowns
export interface BoundarySimpleItem {
  id: number;
  name: string;
  name_en: string | null;
  area_km2: number;
}

export interface BoundarySimpleListResponse {
  total: number;
  items: BoundarySimpleItem[];
}

// Boundary details with full statistics
export interface BoundaryDetails {
  boundary: {
    id: number;
    osm_id: number;
    osm_type: string;
    name: string;
    name_en: string | null;
    admin_level: number;
    parent_id: number | null;
    population: number | null;
    tags: Record<string, any>;
    area_km2: number;
    center: { lat: number; lng: number };
    geometry?: GeoJSON.Geometry;
  };
  statistics: {
    pois: {
      total: number;
      category_types: number;
      by_category: Record<string, number>;
      by_subcategory?: Record<string, Record<string, number>>;
    };
    top_pois: Array<{
      id: number;
      name: string;
      category: string;
      subcategory: string | null;
      address: string | null;
      phone: string | null;
      website: string | null;
      opening_hours: string | null;
      location: { lat: number; lng: number };
    }>;
    buildings: {
      total: number;
      named: number;
    };
    streets: {
      total: number;
      named: number;
      highway_types: number;
      by_highway_type?: Record<string, number>;
      top_streets?: Array<{
        name: string;
        highway_type: string;
        length_m: number;
      }>;
    };
    reports: {
      total: number;
      by_status: Record<string, number>;
    };
  };
}

// Multi-boundary response
export interface MultiBoundaryResponse {
  boundaries: Array<{
    id: number;
    osm_id: number;
    name: string;
    name_en: string | null;
    admin_level: number;
    population: number | null;
    tags: Record<string, any>;
    area_km2: number;
    center: { lat: number; lng: number };
    geometry?: GeoJSON.Geometry;
  }>;
  summary: {
    count: number;
    total_area_km2: number;
    total_population: number;
    total_pois: number;
  };
}

// Urban Data Integration Types (Weather, AQI, Traffic)
export interface UrbanDataWeather {
  temperature: number | null;
  humidity: number | null;
  pressure: number | null;
  wind_speed: number | null;
  description: string | null;
  weather_type: string | null;
  feels_like: number | null;
  clouds: number | null;
  source: string;
  ngsi_ld_id: string | null;
}

export interface UrbanDataAQILevel {
  text: string;
  text_en: string;
  color: string;
  health_advice: string;
}

export interface UrbanDataAQI {
  aqi: number;
  level: UrbanDataAQILevel;
  pm25: number | null;
  pm10: number | null;
  o3: number | null;
  no2: number | null;
  so2: number | null;
  co: number | null;
  source: string;
  ngsi_ld_id: string | null;
}

export interface UrbanDataTrafficLevel {
  text: string;
  text_en: string;
  color: string;
  icon: string;
}

export interface UrbanDataTraffic {
  current_speed: number;
  free_flow_speed: number;
  congestion_percent: number;
  congestion_level: UrbanDataTrafficLevel;
  travel_time: number | null;
  confidence: number | null;
  road_closed: boolean;
  source: string;
  ngsi_ld_id: string | null;
  note: string;
}

export interface UrbanDataResponse {
  boundary: {
    id: number;
    name: string;
    centroid: {
      latitude: number;
      longitude: number;
    };
    area_km2: number | null;
  };
  timestamp: string;
  weather: UrbanDataWeather | null;
  air_quality: UrbanDataAQI | null;
  traffic: UrbanDataTraffic | null;
  lod_context: {
    description: string;
    sources: Array<{ name: string; type: string }>;
    standards: string[];
  };
}

export interface GeoJSONFeature {
  type: 'Feature';
  id?: string;
  geometry: {
    type: string;
    coordinates: any;
  };
  properties: Record<string, any>;
}

export interface GeoJSONFeatureCollection {
  type: 'FeatureCollection';
  features: GeoJSONFeature[];
}

export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  phone: string | null;
  avatar: string | null;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
}

// ============================================
// Report API
// ============================================

export const reportApi = {
  getStatistics: async (): Promise<ReportStatistics> => {
    return apiClient.get<ReportStatistics>('/reports/statistics');
  },

  getReports: async (params?: {
    skip?: number;
    limit?: number;
    status?: string;
    category?: string;
    priority?: string;
    district_id?: number;
    search?: string;
  }): Promise<ReportListResponse> => {
    return apiClient.get<ReportListResponse>('/reports/', params);
  },

  getReport: async (id: number): Promise<Report> => {
    return apiClient.get<Report>(`/reports/${id}`);
  },

  getNearbyReports: async (
    lat: number,
    lng: number,
    radius: number = 1000,
    limit: number = 20
  ): Promise<NearbyReportsResponse> => {
    return apiClient.get<NearbyReportsResponse>('/reports/nearby', {
      lat,
      lng,
      radius,
      limit,
    });
  },

  createReport: async (data: {
    title: string;
    description: string;
    category: string;
    subcategory?: string;
    latitude: number;
    longitude: number;
    address?: string;
    district_id?: number;
    user_id?: number;
  }): Promise<{ id: number; message: string; status: string }> => {
    return apiClient.post('/reports/', data);
  },

  updateStatus: async (
    id: number,
    status: string
  ): Promise<{ message: string; status: string }> => {
    return apiClient.patch(`/reports/${id}/status`, null, { params: { new_status: status } });
  },
};

// ============================================
// Facility API
// ============================================

export const facilityApi = {
  getFacilities: async (params?: {
    category?: string;
    district_id?: number;
    search?: string;
    page?: number;
    limit?: number;
  }): Promise<FacilityListResponse> => {
    // TODO: Backend facilities endpoint not implemented yet
    return { facilities: [], total: 0, page: params?.page || 1, limit: params?.limit || 20 };
  },

  getFacility: async (_id: number): Promise<Facility> => {
    // TODO: Backend facilities endpoint not implemented yet
    throw new Error('Facility endpoint not available');
  },

  getNearbyFacilities: async (
    lat: number,
    lng: number,
    radius: number = 1000,
    _category?: string,
    _limit: number = 20
  ): Promise<NearbyFacilitiesResponse> => {
    // TODO: Backend nearby facilities endpoint not implemented yet
    return { 
      center_lat: lat,
      center_lng: lng,
      radius_meters: radius,
      facilities: [],
      total: 0
    };
  },

  getCategories: async (): Promise<{ categories: Array<{ value: string; label: string }> }> => {
    // TODO: Backend facilities categories endpoint not implemented yet
    return { categories: [] };
  },

  getTransportFacilities: async (params?: {
    facility_type?: string;
    district_id?: number;
    search?: string;
    skip?: number;
    limit?: number;
  }): Promise<{ facilities: any[]; total: number }> => {
    return apiClient.get('/facilities/transport', params);
  },

  getNearbyTransport: async (
    lat: number,
    lng: number,
    radius: number = 500,
    facility_type?: string,
    limit: number = 20
  ): Promise<any> => {
    return apiClient.get('/facilities/transport/nearby', {
      lat,
      lng,
      radius,
      facility_type,
      limit,
    });
  },
};

// ============================================
// Geographic API
// ============================================

export const geographicApi = {
  getBoundaries: async (params?: {
    admin_level?: number;
    parent_id?: number;
    search?: string;
    skip?: number;
    limit?: number;
  }): Promise<BoundaryListResponse> => {
    return apiClient.get<BoundaryListResponse>('/geographic/boundaries', params);
  },

  getBoundariesGeoJSON: async (params?: {
    admin_level?: number;
    parent_id?: number;
    simplify_tolerance?: number;
    districts_only?: boolean;
  }): Promise<GeoJSONFeatureCollection> => {
    return apiClient.get<GeoJSONFeatureCollection>('/geographic/boundaries/geojson', params);
  },

  // Get Hanoi boundary as union of all wards/communes (more accurate boundary)
  getHanoiUnionBoundary: async (params?: {
    simplify_tolerance?: number;
  }): Promise<{
    type: 'Feature';
    id: string;
    geometry: GeoJSON.Geometry;
    properties: {
      name: string;
      name_en: string;
      description: string;
      area_km2: number;
      num_points: number;
      num_wards: number;
      simplify_tolerance: number;
    };
  }> => {
    return apiClient.get('/geographic/boundaries/hanoi-union', params);
  },

  getBoundary: async (
    id: number,
    include_geometry: boolean = false
  ): Promise<Boundary> => {
    return apiClient.get<Boundary>(`/geographic/boundaries/${id}`, { include_geometry });
  },

  getBoundaryContainingPoint: async (
    lat: number,
    lng: number,
    admin_level?: number
  ): Promise<{
    point: { latitude: number; longitude: number };
    boundaries: Array<{
      id: number;
      name: string;
      name_en: string | null;
      admin_level: number;
      admin_level_name: string;
    }>;
  }> => {
    return apiClient.get('/geographic/boundaries/containing-point', {
      latitude: lat,
      longitude: lng,
      admin_level,
    });
  },

  getStreets: async (params?: {
    district_id?: number;
    street_type?: string;
    search?: string;
    skip?: number;
    limit?: number;
  }): Promise<any[]> => {
    return apiClient.get('/geographic/streets', params);
  },

  getNearbyStreets: async (
    lat: number,
    lng: number,
    radius: number = 500,
    limit: number = 20
  ): Promise<any> => {
    return apiClient.get('/geographic/streets/nearby', {
      lat,
      lng,
      radius,
      limit,
    });
  },

  // Get simple list for dropdowns
  getBoundariesListSimple: async (
    admin_level: number = 6
  ): Promise<BoundarySimpleListResponse> => {
    return apiClient.get<BoundarySimpleListResponse>('/geographic/boundaries/list/simple', {
      admin_level,
    });
  },

  // Get detailed info for a single boundary
  getBoundaryDetails: async (
    id: number,
    include_geometry: boolean = true,
    simplify_tolerance: number = 0.0005
  ): Promise<BoundaryDetails> => {
    return apiClient.get<BoundaryDetails>(`/geographic/boundaries/${id}/details`, {
      include_geometry,
      simplify_tolerance,
    });
  },

  // Get details for multiple boundaries
  getMultiBoundaryDetails: async (
    boundary_ids: number[],
    include_geometry: boolean = true,
    simplify_tolerance: number = 0.001
  ): Promise<MultiBoundaryResponse> => {
    return apiClient.post<MultiBoundaryResponse>(
      `/geographic/boundaries/multi-details?include_geometry=${include_geometry}&simplify_tolerance=${simplify_tolerance}`,
      boundary_ids
    );
  },

  // Get urban data (weather, AQI, traffic) for a boundary
  // Note: Traffic data from TomTom is real-time only, not stored in database
  getUrbanData: async (boundaryId: number): Promise<UrbanDataResponse> => {
    return apiClient.get<UrbanDataResponse>(`/geographic/boundaries/${boundaryId}/urban-data`);
  },
};

// ============================================
// Auth API
// ============================================

export const authApi = {
  login: async (username: string, password: string): Promise<LoginResponse> => {
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1'}/auth/login`,
      {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData,
      }
    );

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    return response.json();
  },

  register: async (data: {
    email: string;
    username: string;
    password: string;
    full_name?: string;
    phone?: string;
  }): Promise<User> => {
    return apiClient.post<User>('/auth/register', data);
  },

  getCurrentUser: async (): Promise<User> => {
    return apiClient.get<User>('/users/me');
  },
};

// ============================================
// User API
// ============================================

export const userApi = {
  getUsers: async (params?: {
    skip?: number;
    limit?: number;
    search?: string;
  }): Promise<{ users: User[]; total: number }> => {
    return apiClient.get('/users/', params);
  },

  getUser: async (id: number): Promise<User> => {
    return apiClient.get<User>(`/users/${id}`);
  },

  updateUser: async (
    id: number,
    data: Partial<User>
  ): Promise<User> => {
    return apiClient.put<User>(`/users/${id}`, data);
  },
};

// ============================================
// Health Check
// ============================================

export const healthApi = {
  check: async (): Promise<{ status: string; version: string }> => {
    const response = await fetch(
      `${process.env.NEXT_PUBLIC_API_BASE_URL?.replace('/api/v1', '') || 'http://localhost:8000'}/health`
    );
    return response.json();
  },
};

// ============================================
// Realtime API (Layer 2 - Urban Infrastructure)
// ============================================

export interface WeatherData {
  timestamp: string;
  source: string;
  location: {
    latitude: number;
    longitude: number;
    city: string;
    country: string;
  };
  weather: {
    temperature: number;
    feels_like: number | null;
    humidity: number;
    pressure: number;
    description: string;
    wind_speed: number;
    clouds: number | null;
    visibility: number | null;
  };
}

export interface AirQualityData {
  timestamp: string;
  source: string;
  location: {
    latitude: number;
    longitude: number;
    city: string;
    country: string;
    station: string;
  };
  aqi: {
    value: number;
    level: string;
    color: string;
    description: string;
    health_implications: string;
  };
  pollutants: {
    pm25: { value: number | null; unit: string; description: string };
    pm10: { value: number | null; unit: string; description: string };
    o3: { value: number | null; unit: string; description: string };
    no2: { value: number | null; unit: string; description: string };
    so2: { value: number | null; unit: string; description: string };
    co: { value: number | null; unit: string; description: string };
  };
}

export interface TrafficHotspot {
  name: string;
  location: {
    latitude: number;
    longitude: number;
  };
  traffic: {
    current_speed: number;
    free_flow_speed: number;
    congestion_level: 'free_flow' | 'light' | 'moderate' | 'heavy' | 'severe';
  };
}

export interface GeographicStatistics {
  administrative_boundaries: {
    total: number;
    phuong?: number;
    xa?: number;
  };
  streets: {
    total: number;
    named: number;
    bbox: string;
  };
  buildings: {
    total: number;
    named: number;
    bbox: string;
  };
  pois: {
    total: number;
    bbox: string;
  };
  summary: {
    total_features: number;
    data_source: string;
    city: string;
    last_updated: string;
  };
}

export const realtimeApi = {
  getWeather: async (): Promise<WeatherData> => {
    return apiClient.get<WeatherData>('/realtime/weather/latest');
  },

  getAirQuality: async (): Promise<AirQualityData> => {
    return apiClient.get<AirQualityData>('/realtime/air-quality/latest');
  },

  getTrafficHotspots: async (): Promise<{ hotspots: TrafficHotspot[]; count: number }> => {
    return apiClient.get('/realtime/traffic/hotspots');
  },

  getWeatherMultiCity: async (): Promise<{ cities: WeatherData[] }> => {
    return apiClient.get('/realtime/weather/cities');
  },

  getAirQualityMultiCity: async (): Promise<{ cities: AirQualityData[] }> => {
    return apiClient.get('/realtime/air-quality/cities');
  },
};

export const geographicStatsApi = {
  getStatistics: async (): Promise<GeographicStatistics> => {
    return apiClient.get<GeographicStatistics>('/geographic/statistics');
  },
};
