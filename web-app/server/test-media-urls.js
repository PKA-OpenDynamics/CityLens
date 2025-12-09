// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

/**
 * Test script to verify media URLs are accessible
 * Run: node server/test-media-urls.js
 */

import { connectToDatabase } from './config/db.js';
import dotenv from 'dotenv';

dotenv.config();

const SERVER_URL = process.env.SERVER_URL || 'http://localhost:3001';

async function testMediaUrls() {
  try {
    console.log('🔍 Connecting to MongoDB...');
    const { db } = await connectToDatabase();
    console.log('✅ Connected to MongoDB\n');

    const reportsCollection = db.collection('reports');

    // Get latest report
    console.log('📋 Fetching latest report...');
    const latestReport = await reportsCollection.findOne({}, { sort: { createdAt: -1 } });

    if (!latestReport) {
      console.log('⚠️  No reports found in database');
      return;
    }

    console.log(`\n${'='.repeat(60)}`);
    console.log('📌 Latest Report:');
    console.log(`${'='.repeat(60)}`);
    console.log(`ID: ${latestReport._id}`);
    console.log(`Type: ${latestReport.reportType}`);
    console.log(`Content: ${latestReport.content.substring(0, 100)}...`);
    console.log(`Media Count: ${latestReport.media?.length || 0}\n`);

    if (!latestReport.media || latestReport.media.length === 0) {
      console.log('⚠️  No media files in this report');
      return;
    }

    console.log(`${'='.repeat(60)}`);
    console.log('🔗 Media URLs:');
    console.log(`${'='.repeat(60)}\n`);

    for (let i = 0; i < latestReport.media.length; i++) {
      const media = latestReport.media[i];
      const reportId = latestReport._id.toString();
      
      console.log(`Media #${i + 1}:`);
      console.log(`  Type: ${media.type}`);
      console.log(`  Original URI: ${media.uri.substring(0, 80)}...`);
      
      // Generate URL
      let mediaUrl = null;
      if (media.uri.startsWith('data:')) {
        mediaUrl = `${SERVER_URL}/api/media/report/${reportId}/${i}`;
        console.log(`  ✅ Generated URL: ${mediaUrl}`);
      } else if (media.uri.startsWith('http://') || media.uri.startsWith('https://')) {
        mediaUrl = media.uri;
        console.log(`  ✅ HTTP URL: ${mediaUrl}`);
      } else if (media.uri.startsWith('blob:')) {
        console.log(`  ⚠️  Blob URL - cannot be accessed from server`);
        console.log(`  💡 Should be converted to base64 before saving`);
        continue;
      } else {
        console.log(`  ⚠️  Unknown URI format`);
        continue;
      }

      // Test URL accessibility
      if (mediaUrl) {
        console.log(`  🔍 Testing URL accessibility...`);
        try {
          const response = await fetch(mediaUrl);
          
          if (response.ok) {
            const contentType = response.headers.get('content-type');
            const contentLength = response.headers.get('content-length');
            console.log(`  ✅ URL is accessible!`);
            console.log(`     Content-Type: ${contentType}`);
            console.log(`     Content-Length: ${contentLength} bytes`);
            console.log(`     Status: ${response.status} ${response.statusText}`);
            
            // For images, verify it's actually an image
            if (media.type === 'image' && contentType?.startsWith('image/')) {
              console.log(`     ✅ Valid image format`);
            } else if (media.type === 'video' && contentType?.startsWith('video/')) {
              console.log(`     ✅ Valid video format`);
            } else {
              console.log(`     ⚠️  Content-Type doesn't match media type`);
            }
            
            // Try to get a small preview (first few bytes)
            const buffer = await response.arrayBuffer();
            console.log(`     Data received: ${buffer.byteLength} bytes`);
          } else {
            console.log(`  ❌ URL returned error: ${response.status} ${response.statusText}`);
          }
        } catch (fetchError) {
          console.log(`  ❌ Error fetching URL: ${fetchError.message}`);
          console.log(`     Make sure server is running at ${SERVER_URL}`);
        }
      }
      
      console.log('');
    }

    console.log(`${'='.repeat(60)}`);
    console.log('📝 Instructions:');
    console.log(`${'='.repeat(60)}`);
    console.log('1. Copy any URL above and paste in browser to view media');
    console.log(`2. Example: ${SERVER_URL}/api/media/report/${latestReport._id}/0`);
    console.log('3. The URL should display the image/video directly');
    console.log(`\n✅ Test completed!\n`);

  } catch (error) {
    console.error('❌ Error testing media URLs:', error);
    process.exit(1);
  }
}

// Run test
testMediaUrls()
  .then(() => {
    process.exit(0);
  })
  .catch((error) => {
    console.error('Test failed:', error);
    process.exit(1);
  });

