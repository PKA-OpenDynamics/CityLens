// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

/**
 * Test script to fetch and verify reports from MongoDB
 * Run: node server/test-reports.js
 */

import { connectToDatabase } from './config/db.js';
import dotenv from 'dotenv';

dotenv.config();

async function testReports() {
  try {
    console.log('🔍 Connecting to MongoDB...');
    const { db } = await connectToDatabase();
    console.log('✅ Connected to MongoDB\n');

    const reportsCollection = db.collection('reports');

    // Get all reports
    console.log('📋 Fetching all reports...');
    const allReports = await reportsCollection.find({}).sort({ createdAt: -1 }).toArray();
    console.log(`Found ${allReports.length} reports\n`);

    if (allReports.length === 0) {
      console.log('⚠️  No reports found in database');
      return;
    }

    // Display each report
    allReports.forEach((report, index) => {
      console.log(`\n${'='.repeat(60)}`);
      console.log(`Report #${index + 1}`);
      console.log(`${'='.repeat(60)}`);
      console.log(`ID: ${report._id}`);
      console.log(`Type: ${report.reportType}`);
      console.log(`Ward: ${report.ward}`);
      console.log(`Address Detail: ${report.addressDetail || 'N/A'}`);
      console.log(`Location: ${report.location ? `${report.location.lat}, ${report.location.lng}` : 'N/A'}`);
      console.log(`Title: ${report.title || 'N/A'}`);
      console.log(`Content: ${report.content.substring(0, 100)}${report.content.length > 100 ? '...' : ''}`);
      console.log(`Status: ${report.status}`);
      console.log(`Media Count: ${report.media?.length || 0}`);
      
      // Display media details
      if (report.media && report.media.length > 0) {
        console.log('\nMedia Files:');
        report.media.forEach((media, mediaIndex) => {
          console.log(`  ${mediaIndex + 1}. Type: ${media.type}, URI: ${media.uri.substring(0, 50)}...`);
          if (media.filename) {
            console.log(`     Filename: ${media.filename}`);
          }
        });
      }

      console.log(`Created At: ${new Date(report.createdAt).toLocaleString()}`);
      console.log(`Updated At: ${new Date(report.updatedAt).toLocaleString()}`);
    });

    // Test fetching by status
    console.log(`\n${'='.repeat(60)}`);
    console.log('📊 Reports by Status:');
    console.log(`${'='.repeat(60)}`);
    
    const statuses = ['pending', 'processing', 'resolved', 'rejected'];
    for (const status of statuses) {
      const count = await reportsCollection.countDocuments({ status });
      console.log(`${status}: ${count}`);
    }

    // Test fetching latest report
    console.log(`\n${'='.repeat(60)}`);
    console.log('📌 Latest Report:');
    console.log(`${'='.repeat(60)}`);
    const latestReport = await reportsCollection.findOne({}, { sort: { createdAt: -1 } });
    if (latestReport) {
      console.log(`ID: ${latestReport._id}`);
      console.log(`Type: ${latestReport.reportType}`);
      console.log(`Content: ${latestReport.content.substring(0, 200)}...`);
      console.log(`Media: ${latestReport.media?.length || 0} files`);
      
      // Verify media URIs are accessible (for images)
      if (latestReport.media && latestReport.media.length > 0) {
        console.log('\n🔍 Verifying media files...');
        for (const media of latestReport.media) {
          const uriPreview = media.uri.length > 80 ? media.uri.substring(0, 80) + '...' : media.uri;
          console.log(`  ${media.type}: ${uriPreview}`);
          
          if (media.type === 'image' || media.type === 'video') {
            try {
              // Check URI format
              const isBlobUrl = media.uri.startsWith('blob:');
              const isDataUrl = media.uri.startsWith('data:');
              const isHttpUrl = media.uri.startsWith('http://') || media.uri.startsWith('https://');
              const isFileUrl = media.uri.startsWith('file:');
              
              if (isBlobUrl) {
                console.log(`    ⚠️  Blob URL detected - will not be accessible from server`);
                console.log(`    💡 Should be converted to base64 data URL before saving`);
              } else if (isDataUrl) {
                const base64Length = media.uri.includes(',') ? media.uri.split(',')[1].length : 0;
                console.log(`    ✅ Base64 data URL (length: ${base64Length} chars)`);
                console.log(`    ✅ Can be used directly - no conversion needed`);
              } else if (isHttpUrl) {
                console.log(`    ✅ HTTP/HTTPS URL - accessible if publicly available`);
              } else if (isFileUrl) {
                console.log(`    ⚠️  File URL - may not be accessible from server`);
              } else {
                console.log(`    ⚠️  Unknown URI format`);
              }
            } catch (error) {
              console.log(`    ❌ Error checking URI: ${error.message}`);
            }
          }
        }
      }
    }

    console.log(`\n${'='.repeat(60)}`);
    console.log('✅ Test completed successfully!');
    console.log(`${'='.repeat(60)}\n`);

  } catch (error) {
    console.error('❌ Error testing reports:', error);
    process.exit(1);
  }
}

// Run test
testReports()
  .then(() => {
    console.log('Test finished');
    process.exit(0);
  })
  .catch((error) => {
    console.error('Test failed:', error);
    process.exit(1);
  });

