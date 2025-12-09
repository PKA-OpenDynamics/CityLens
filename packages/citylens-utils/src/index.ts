// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)
/**
 * CityLens Utils - Tiện ích xử lý dữ liệu đô thị thông minh
 * 
 * Thư viện này cung cấp các hàm tiện ích cho việc xử lý dữ liệu trong
 * nền tảng CityLens Smart City.
 * 
 * Copyright (C) 2025 CityLens Team
 * 
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 */

// ============================================================
// Tiện ích xử lý tọa độ địa lý
// ============================================================

/**
 * Tính khoảng cách giữa hai điểm tọa độ (Haversine formula)
 * @param lat1 Vĩ độ điểm 1
 * @param lon1 Kinh độ điểm 1
 * @param lat2 Vĩ độ điểm 2
 * @param lon2 Kinh độ điểm 2
 * @returns Khoảng cách tính bằng km
 */
export function calculateDistance(
  lat1: number,
  lon1: number,
  lat2: number,
  lon2: number
): number {
  const R = 6371; // Bán kính Trái Đất (km)
  const dLat = toRadians(lat2 - lat1);
  const dLon = toRadians(lon2 - lon1);
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(toRadians(lat1)) *
      Math.cos(toRadians(lat2)) *
      Math.sin(dLon / 2) *
      Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
}

/**
 * Chuyển đổi độ sang radian
 */
export function toRadians(degrees: number): number {
  return degrees * (Math.PI / 180);
}

/**
 * Chuyển đổi radian sang độ
 */
export function toDegrees(radians: number): number {
  return radians * (180 / Math.PI);
}

/**
 * Kiểm tra tọa độ có hợp lệ không
 */
export function isValidCoordinate(lat: number, lon: number): boolean {
  return lat >= -90 && lat <= 90 && lon >= -180 && lon <= 180;
}

// ============================================================
// Tiện ích xử lý NGSI-LD Entity ID
// ============================================================

/**
 * Tạo NGSI-LD Entity ID theo chuẩn
 * @param entityType Loại entity (VD: CivicIssue, AirQualityObserved)
 * @param id ID duy nhất
 * @returns URN theo chuẩn NGSI-LD
 */
export function createNgsiLdId(entityType: string, id: string | number): string {
  return `urn:ngsi-ld:${entityType}:${id}`;
}

/**
 * Phân tích NGSI-LD Entity ID
 * @param urn URN đầy đủ
 * @returns Object chứa entityType và id
 */
export function parseNgsiLdId(urn: string): { entityType: string; id: string } | null {
  const pattern = /^urn:ngsi-ld:([^:]+):(.+)$/;
  const match = urn.match(pattern);
  if (match) {
    return {
      entityType: match[1],
      id: match[2],
    };
  }
  return null;
}

/**
 * Kiểm tra URN có đúng chuẩn NGSI-LD không
 */
export function isValidNgsiLdUrn(urn: string): boolean {
  return /^urn:ngsi-ld:[^:]+:.+$/.test(urn);
}

// ============================================================
// Tiện ích xử lý chỉ số chất lượng không khí (AQI)
// ============================================================

export enum AqiLevel {
  GOOD = 'good',
  MODERATE = 'moderate',
  UNHEALTHY_SENSITIVE = 'unhealthy_sensitive',
  UNHEALTHY = 'unhealthy',
  VERY_UNHEALTHY = 'very_unhealthy',
  HAZARDOUS = 'hazardous',
}

export interface AqiInfo {
  level: AqiLevel;
  label: string;
  labelVi: string;
  color: string;
  advice: string;
}

/**
 * Lấy thông tin mức độ AQI
 * @param aqi Chỉ số AQI (0-500)
 * @returns Thông tin chi tiết về mức độ AQI
 */
export function getAqiInfo(aqi: number): AqiInfo {
  if (aqi <= 50) {
    return {
      level: AqiLevel.GOOD,
      label: 'Good',
      labelVi: 'Tốt',
      color: '#00e400',
      advice: 'Chất lượng không khí tốt, phù hợp cho mọi hoạt động ngoài trời.',
    };
  } else if (aqi <= 100) {
    return {
      level: AqiLevel.MODERATE,
      label: 'Moderate',
      labelVi: 'Trung bình',
      color: '#ffff00',
      advice: 'Chất lượng không khí chấp nhận được. Người nhạy cảm nên hạn chế hoạt động ngoài trời.',
    };
  } else if (aqi <= 150) {
    return {
      level: AqiLevel.UNHEALTHY_SENSITIVE,
      label: 'Unhealthy for Sensitive Groups',
      labelVi: 'Không lành mạnh cho nhóm nhạy cảm',
      color: '#ff7e00',
      advice: 'Trẻ em, người già và người có bệnh hô hấp nên hạn chế hoạt động ngoài trời.',
    };
  } else if (aqi <= 200) {
    return {
      level: AqiLevel.UNHEALTHY,
      label: 'Unhealthy',
      labelVi: 'Không lành mạnh',
      color: '#ff0000',
      advice: 'Mọi người có thể bắt đầu gặp vấn đề sức khỏe. Hạn chế hoạt động ngoài trời.',
    };
  } else if (aqi <= 300) {
    return {
      level: AqiLevel.VERY_UNHEALTHY,
      label: 'Very Unhealthy',
      labelVi: 'Rất không lành mạnh',
      color: '#8f3f97',
      advice: 'Cảnh báo sức khỏe nghiêm trọng. Tránh hoạt động ngoài trời.',
    };
  } else {
    return {
      level: AqiLevel.HAZARDOUS,
      label: 'Hazardous',
      labelVi: 'Nguy hiểm',
      color: '#7e0023',
      advice: 'Tình trạng khẩn cấp. Toàn bộ dân số bị ảnh hưởng. Ở trong nhà.',
    };
  }
}

// ============================================================
// Tiện ích format dữ liệu
// ============================================================

/**
 * Format số với đơn vị Việt Nam
 * @param num Số cần format
 * @returns Chuỗi đã format (VD: 1.234.567)
 */
export function formatNumberVi(num: number): string {
  return num.toLocaleString('vi-VN');
}

/**
 * Format ngày tháng theo định dạng Việt Nam
 * @param date Date object hoặc ISO string
 * @returns Chuỗi ngày tháng (VD: 24/01/2025 21:30)
 */
export function formatDateVi(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date;
  return d.toLocaleString('vi-VN', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

/**
 * Format khoảng cách thân thiện
 * @param km Khoảng cách tính bằng km
 * @returns Chuỗi đã format (VD: "500 m" hoặc "2,5 km")
 */
export function formatDistance(km: number): string {
  if (km < 1) {
    return `${Math.round(km * 1000)} m`;
  }
  return `${km.toFixed(1).replace('.', ',')} km`;
}

// ============================================================
// Tiện ích xử lý trạng thái báo cáo
// ============================================================

export enum ReportStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  RESOLVED = 'resolved',
  REJECTED = 'rejected',
}

export interface ReportStatusInfo {
  status: ReportStatus;
  label: string;
  labelVi: string;
  color: string;
}

/**
 * Lấy thông tin trạng thái báo cáo
 */
export function getReportStatusInfo(status: ReportStatus): ReportStatusInfo {
  const statusMap: Record<ReportStatus, ReportStatusInfo> = {
    [ReportStatus.PENDING]: {
      status: ReportStatus.PENDING,
      label: 'Pending',
      labelVi: 'Đang chờ xử lý',
      color: '#f59e0b',
    },
    [ReportStatus.IN_PROGRESS]: {
      status: ReportStatus.IN_PROGRESS,
      label: 'In Progress',
      labelVi: 'Đang xử lý',
      color: '#3b82f6',
    },
    [ReportStatus.RESOLVED]: {
      status: ReportStatus.RESOLVED,
      label: 'Resolved',
      labelVi: 'Đã giải quyết',
      color: '#10b981',
    },
    [ReportStatus.REJECTED]: {
      status: ReportStatus.REJECTED,
      label: 'Rejected',
      labelVi: 'Từ chối',
      color: '#ef4444',
    },
  };
  return statusMap[status] || statusMap[ReportStatus.PENDING];
}

// ============================================================
// Xuất tất cả
// ============================================================

export const VERSION = '1.0.0';
