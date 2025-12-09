// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import express from 'express';
import { ObjectId } from 'mongodb';
import { connectToDatabase } from '../config/db.js';
import {
  createUserProfile,
  hashPassword,
  comparePassword,
  sanitizeUserProfile,
} from '../models/UserProfile.js';
import jwt from 'jsonwebtoken';

const router = express.Router();
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key-change-in-production';
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '7d';

/**
 * POST /api/auth/register
 * Đăng ký người dùng mới
 */
router.post('/register', async (req, res) => {
  try {
    console.log('Register request body:', JSON.stringify(req.body, null, 2));
    const { username, email, password, full_name, phone } = req.body;

    // Validation
    if (!username || !email || !password || !full_name) {
      console.log('Validation failed - missing fields:', { username: !!username, email: !!email, password: !!password, full_name: !!full_name });
      return res.status(400).json({
        success: false,
        error: 'Vui lòng điền đầy đủ thông tin (username, email, password, full_name)',
      });
    }

    if (password.length < 6) {
      return res.status(400).json({
        success: false,
        error: 'Mật khẩu phải có ít nhất 6 ký tự',
      });
    }

    const { db } = await connectToDatabase();
    const collection = db.collection('user_profile');

    // Check if username or email already exists
    const existingUser = await collection.findOne({
      $or: [{ username }, { email }],
    });

    if (existingUser) {
      return res.status(400).json({
        success: false,
        error: existingUser.username === username
          ? 'Tên đăng nhập đã tồn tại'
          : 'Email đã được sử dụng',
      });
    }

    // Hash password
    const hashedPassword = await hashPassword(password);

    // Create user profile
    const userData = createUserProfile({
      username,
      email,
      password: hashedPassword,
      full_name,
      phone: phone || '',
    });

    // Insert into database
    const result = await collection.insertOne(userData);

    // Generate JWT token
    const token = jwt.sign(
      { userId: result.insertedId.toString(), username },
      JWT_SECRET,
      { expiresIn: JWT_EXPIRES_IN }
    );

    // Return user without password
    const user = sanitizeUserProfile(userData);

    res.status(201).json({
      success: true,
      data: {
        user,
        access_token: token,
        token_type: 'bearer',
      },
    });
  } catch (error) {
    console.error('Error registering user:', error);
    console.error('Error stack:', error.stack);
    res.status(500).json({
      success: false,
      error: error.message || 'Không thể đăng ký. Vui lòng thử lại sau.',
    });
  }
});

/**
 * POST /api/auth/login
 * Đăng nhập
 */
router.post('/login', async (req, res) => {
  try {
    const { username, password } = req.body;

    // Validation
    if (!username || !password) {
      return res.status(400).json({
        success: false,
        error: 'Vui lòng nhập tên đăng nhập và mật khẩu',
      });
    }

    const { db } = await connectToDatabase();
    const collection = db.collection('user_profile');

    // Find user by username or email
    const user = await collection.findOne({
      $or: [{ username }, { email: username }],
    });

    if (!user) {
      return res.status(401).json({
        success: false,
        error: 'Tên đăng nhập hoặc mật khẩu không đúng',
      });
    }

    // Check if user is active
    if (!user.is_active) {
      return res.status(401).json({
        success: false,
        error: 'Tài khoản đã bị khóa',
      });
    }

    // Verify password
    const isPasswordValid = await comparePassword(password, user.password);
    if (!isPasswordValid) {
      return res.status(401).json({
        success: false,
        error: 'Tên đăng nhập hoặc mật khẩu không đúng',
      });
    }

    // Update last_login
    await collection.updateOne(
      { _id: user._id },
      { $set: { last_login: new Date(), updated_at: new Date() } }
    );

    // Generate JWT token
    const token = jwt.sign(
      { userId: user._id.toString(), username: user.username },
      JWT_SECRET,
      { expiresIn: JWT_EXPIRES_IN }
    );

    // Return user without password
    const userWithoutPassword = sanitizeUserProfile(user);

    res.json({
      success: true,
      data: {
        access_token: token,
        token_type: 'bearer',
        user: userWithoutPassword,
      },
    });
  } catch (error) {
    console.error('Error logging in:', error);
    res.status(500).json({
      success: false,
      error: 'Không thể đăng nhập. Vui lòng thử lại sau.',
    });
  }
});

/**
 * GET /api/auth/me
 * Lấy thông tin người dùng hiện tại (cần token)
 */
router.get('/me', async (req, res) => {
  try {
    // Get token from Authorization header
    const authHeader = req.headers.authorization;
    if (!authHeader || !authHeader.startsWith('Bearer ')) {
      return res.status(401).json({
        success: false,
        error: 'Chưa đăng nhập',
      });
    }

    const token = authHeader.substring(7);

    // Verify token
    let decoded;
    try {
      decoded = jwt.verify(token, JWT_SECRET);
    } catch (error) {
      return res.status(401).json({
        success: false,
        error: 'Token không hợp lệ hoặc đã hết hạn',
      });
    }

    const { db } = await connectToDatabase();
    const collection = db.collection('user_profile');

    // Find user by ID
    const user = await collection.findOne({ _id: new ObjectId(decoded.userId) });

    if (!user) {
      return res.status(404).json({
        success: false,
        error: 'Không tìm thấy người dùng',
      });
    }

    // Return user without password
    const userWithoutPassword = sanitizeUserProfile(user);

    res.json({
      success: true,
      data: userWithoutPassword,
    });
  } catch (error) {
    console.error('Error getting user:', error);
    res.status(500).json({
      success: false,
      error: 'Không thể lấy thông tin người dùng',
    });
  }
});

export default router;

