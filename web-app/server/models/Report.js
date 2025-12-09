// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import { ObjectId } from 'mongodb';

/**
 * Report Schema
 */
export const ReportSchema = {
  reportType: String, // Loại phản ánh
  ward: String, // Xã/phường
  addressDetail: String, // Số nhà, thôn/xóm, khu vực
  location: {
    lat: Number,
    lng: Number,
  },
  title: String, // Tiêu đề
  content: String, // Nội dung phản ánh
  media: [
    {
      uri: String, // URL hoặc base64
      type: String, // 'image' hoặc 'video'
      filename: String, // Tên file (optional)
    },
  ],
  userId: String, // ID người dùng (optional, có thể null nếu chưa đăng nhập)
  status: {
    type: String,
    default: 'pending', // pending, processing, resolved, rejected
  },
  createdAt: {
    type: Date,
    default: Date.now,
  },
  updatedAt: {
    type: Date,
    default: Date.now,
  },
};

/**
 * Create a report document
 */
export function createReport(data) {
  return {
    _id: new ObjectId(),
    reportType: data.reportType,
    ward: data.ward,
    addressDetail: data.addressDetail || '',
    location: data.location || null,
    title: data.title || '',
    content: data.content,
    media: data.media || [],
    userId: data.userId || null,
    status: data.status || 'pending',
    createdAt: new Date(),
    updatedAt: new Date(),
  };
}

