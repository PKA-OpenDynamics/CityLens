// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import { ObjectId } from 'mongodb';
import bcrypt from 'bcryptjs';

/**
 * User Profile Schema
 */
export const UserProfileSchema = {
  username: String, // Tên đăng nhập (unique)
  email: String, // Email (unique)
  password: String, // Mật khẩu đã hash
  full_name: String, // Họ và tên
  phone: String, // Số điện thoại (optional)
  is_active: {
    type: Boolean,
    default: true,
  },
  role: {
    type: String,
    default: 'user', // user, admin
  },
  level: {
    type: Number,
    default: 1,
  },
  points: {
    type: Number,
    default: 0,
  },
  reputation_score: {
    type: Number,
    default: 0,
  },
  is_verified: {
    type: Boolean,
    default: false,
  },
  is_admin: {
    type: Boolean,
    default: false,
  },
  created_at: {
    type: Date,
    default: Date.now,
  },
  last_login: Date,
  updated_at: {
    type: Date,
    default: Date.now,
  },
};

/**
 * Create a user profile document
 */
export function createUserProfile(data) {
  return {
    _id: new ObjectId(),
    username: data.username,
    email: data.email,
    password: data.password, // Should be hashed before calling this
    full_name: data.full_name,
    phone: data.phone || '',
    is_active: data.is_active !== undefined ? data.is_active : true,
    role: data.role || 'user',
    level: data.level || 1,
    points: data.points || 0,
    reputation_score: data.reputation_score || 0,
    is_verified: data.is_verified || false,
    is_admin: data.is_admin || false,
    created_at: new Date(),
    last_login: null,
    updated_at: new Date(),
  };
}

/**
 * Hash password
 */
export async function hashPassword(password) {
  const saltRounds = 10;
  return await bcrypt.hash(password, saltRounds);
}

/**
 * Compare password
 */
export async function comparePassword(password, hashedPassword) {
  return await bcrypt.compare(password, hashedPassword);
}

/**
 * Sanitize user profile (remove password)
 */
export function sanitizeUserProfile(user) {
  if (!user) return null;
  const { password, ...userWithoutPassword } = user;
  return userWithoutPassword;
}

