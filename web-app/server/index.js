// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import express from 'express';
import cors from 'cors';
import dotenv from 'dotenv';
import reportsRouter from './routes/reports.js';
import mediaRouter from './routes/media.js';
import { connectToDatabase } from './config/db.js';

dotenv.config();

const app = express();
const PORT = process.env.PORT || 3001;
const CORS_ORIGIN = process.env.CORS_ORIGIN || 'http://localhost:8081';

// Middleware
app.use(cors({
  origin: function (origin, callback) {
    // Allow requests with no origin (like mobile apps, Postman, or curl)
    if (!origin) return callback(null, true);
    
    // Allow requests from CORS_ORIGIN or any origin for media endpoints
    if (origin === CORS_ORIGIN || origin.includes('localhost')) {
      return callback(null, true);
    }
    
    // For production, you might want to restrict this
    callback(null, true);
  },
  credentials: true,
}));
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ extended: true, limit: '50mb' }));

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// Routes
app.use('/api/reports', reportsRouter);
app.use('/api/media', mediaRouter);

// Test MongoDB connection on startup
async function testConnection() {
  try {
    await connectToDatabase();
    console.log('✅ Connected to MongoDB Atlas');
  } catch (error) {
    console.error('❌ Failed to connect to MongoDB:', error.message);
    console.error('Please check your MONGODB_URI in .env file');
  }
}

// Start server
app.listen(PORT, async () => {
  console.log(`🚀 Server running on http://localhost:${PORT}`);
  await testConnection();
});

export default app;

