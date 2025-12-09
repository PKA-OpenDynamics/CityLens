// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import express from 'express';
import { connectToDatabase } from '../config/db.js';
import { createReport } from '../models/Report.js';

const router = express.Router();

/**
 * POST /api/reports
 * Tạo một báo cáo mới
 */
router.post('/', async (req, res) => {
  try {
    const { db } = await connectToDatabase();
    const reportsCollection = db.collection('reports');

    const reportData = {
      reportType: req.body.reportType,
      ward: req.body.ward,
      addressDetail: req.body.addressDetail || '',
      location: req.body.location || null,
      title: req.body.title || '',
      content: req.body.content,
      media: req.body.media || [],
      userId: req.body.userId || null,
      status: 'pending',
    };

    const report = createReport(reportData);
    const result = await reportsCollection.insertOne(report);

    res.status(201).json({
      success: true,
      data: {
        id: result.insertedId.toString(),
        ...report,
        _id: result.insertedId.toString(),
      },
    });
  } catch (error) {
    console.error('Error creating report:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to create report',
      message: error.message,
    });
  }
});

/**
 * GET /api/reports
 * Lấy danh sách báo cáo
 */
router.get('/', async (req, res) => {
  try {
    const { db } = await connectToDatabase();
    const reportsCollection = db.collection('reports');

    const limit = parseInt(req.query.limit) || 20;
    const skip = parseInt(req.query.skip) || 0;
    const status = req.query.status;

    const query = status ? { status } : {};

    const reports = await reportsCollection
      .find(query)
      .sort({ createdAt: -1 })
      .limit(limit)
      .skip(skip)
      .toArray();

    res.json({
      success: true,
      data: reports,
      count: reports.length,
    });
  } catch (error) {
    console.error('Error fetching reports:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch reports',
      message: error.message,
    });
  }
});

/**
 * GET /api/reports/:id
 * Lấy một báo cáo cụ thể
 */
router.get('/:id', async (req, res) => {
  try {
    const { db } = await connectToDatabase();
    const reportsCollection = db.collection('reports');
    const { ObjectId } = await import('mongodb');

    const report = await reportsCollection.findOne({
      _id: new ObjectId(req.params.id),
    });

    if (!report) {
      return res.status(404).json({
        success: false,
        error: 'Report not found',
      });
    }

    res.json({
      success: true,
      data: report,
    });
  } catch (error) {
    console.error('Error fetching report:', error);
    res.status(500).json({
      success: false,
      error: 'Failed to fetch report',
      message: error.message,
    });
  }
});

export default router;

