// Copyright (c) 2025 CityLens Contributors
// Licensed under the MIT License

/**
 * API Types
 */

export interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  phone?: string;
  level: number;
  points: number;
  reputation_score: number;
  is_active: boolean;
  is_verified: boolean;
  is_admin: boolean;
  created_at: string;
  last_login?: string;
}

export enum IncidentType {
  FLOOD = 'ngap_nuoc',
  TRAFFIC_JAM = 'ket_xe',
  POOR_AQI = 'aqi_kem',
  ACCIDENT = 'tai_nan',
  ROAD_DAMAGE = 'duong_hong',
  HIGH_TIDE = 'trieu_cuong',
  OTHER = 'khac',
}

export enum ReportStatus {
  PENDING = 'cho_xac_nhan',
  VERIFIED = 'da_xac_nhan',
  REJECTED = 'tu_choi',
  RESOLVED = 'da_giai_quyet',
}

export interface Report {
  id: number;
  user_id: number;
  incident_type: IncidentType;
  title: string;
  description?: string;
  severity: number;
  latitude: number;
  longitude: number;
  address?: string;
  district?: string;
  city: string;
  status: ReportStatus;
  confidence_score: number;
  verification_count: number;
  incident_time: string;
  created_at: string;
  updated_at?: string;
  resolved_at?: string;
  user_username?: string;
}

export enum AlertLevel {
  INFO = 'thong_tin',
  WARNING = 'canh_bao',
  DANGER = 'nguy_hiem',
  CRITICAL = 'khan_cap',
}

export interface Incident {
  id: number;
  incident_type: string;
  title: string;
  description?: string;
  alert_level: AlertLevel;
  severity_score: number;
  latitude: number;
  longitude: number;
  affected_radius: number;
  address?: string;
  district?: string;
  source_type: string;
  confirmation_count: number;
  is_active: boolean;
  start_time: string;
  end_time?: string;
  created_at: string;
}

export interface Statistics {
  total_reports: number;
  pending_reports: number;
  verified_reports: number;
  active_incidents: number;
  active_users: number;
}

export interface ApiResponse<T> {
  data: T;
  message?: string;
  success: boolean;
}
