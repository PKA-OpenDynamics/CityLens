// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import express from 'express';
import { connectToDatabase } from '../config/db.js';
import { ObjectId } from 'mongodb';

const router = express.Router();

/**
 * GET /api/media/report/:reportId/:mediaIndex
 * Serve media file from report (convert base64 data URI to image/video response)
 */
router.get('/report/:reportId/:mediaIndex', async (req, res) => {
  try {
    const { db } = await connectToDatabase();
    const reportsCollection = db.collection('reports');
    
    const reportId = req.params.reportId;
    const mediaIndex = parseInt(req.params.mediaIndex);

    const report = await reportsCollection.findOne({
      _id: new ObjectId(reportId),
    });

    if (!report) {
      return res.status(404).json({
        success: false,
        error: 'Report not found',
      });
    }

    if (!report.media || !report.media[mediaIndex]) {
      return res.status(404).json({
        success: false,
        error: 'Media not found',
      });
    }

    const media = report.media[mediaIndex];
    const uri = media.uri;

    // Handle base64 data URI
    if (uri.startsWith('data:')) {
      const matches = uri.match(/^data:([^;]+);base64,(.+)$/);
      if (matches) {
        const mimeType = matches[1];
        const base64Data = matches[2];
        
        // Convert base64 to buffer
        const buffer = Buffer.from(base64Data, 'base64');
        
        // Set appropriate headers
        res.setHeader('Content-Type', mimeType);
        res.setHeader('Content-Length', buffer.length);
        res.setHeader('Cache-Control', 'public, max-age=31536000'); // Cache for 1 year
        
        // Send buffer as response
        return res.send(buffer);
      }
    }

    // Handle HTTP/HTTPS URLs (redirect or proxy)
    if (uri.startsWith('http://') || uri.startsWith('https://')) {
      return res.redirect(uri);
    }

    // Handle blob URLs (not accessible from server)
    if (uri.startsWith('blob:')) {
      return res.status(400).json({
        success: false,
        error: 'Blob URLs are not accessible from server. Media should be stored as base64 data URI.',
      });
    }

    // Unknown format
    return res.status(400).json({
      success: false,
      error: 'Unsupported media format',
    });

  } catch (error) {
    console.error('Error serving media:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to serve media',
      message: error.message,
    });
  }
});

export default router;

