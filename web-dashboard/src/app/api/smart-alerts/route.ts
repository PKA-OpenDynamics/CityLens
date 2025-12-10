// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

/**
 * Smart Alerts API Route
 * Uses Gemini AI to analyze city data and generate intelligent alerts
 */

import { NextRequest, NextResponse } from 'next/server';
import { GoogleGenerativeAI } from '@google/generative-ai';

const GEMINI_API_KEY = process.env.GEMINI_API_KEY || '';

interface CityMetrics {
  aqi?: number;
  temperature?: number;
  humidity?: number;
  traffic_speed?: number;
  congestion_level?: number;
  pending_issues?: number;
  parking_occupancy?: number;
}

interface GeneratedAlert {
  id: string;
  type: 'environment' | 'traffic' | 'civic' | 'parking' | 'health' | 'safety';
  severity: 'critical' | 'warning' | 'info';
  title: string;
  description: string;
  ward: string;
  district: string;
  recommendation: string;
  impact: string;
  affectedPopulation: string;
  timestamp: string;
}

// Ward data for Hanoi
const HANOI_WARDS = [
  'Phường Phúc Xá', 'Phường Trúc Bạch', 'Phường Vĩnh Phúc', 'Phường Cống Vị', 'Phường Liễu Giai',
  'Phường Nguyễn Trung Trực', 'Phường Quán Thánh', 'Phường Ngọc Hà', 'Phường Điện Biên', 'Phường Đội Cấn',
  'Phường Ba Đình', 'Phường Kim Mã', 'Phường Giảng Võ', 'Phường Thành Công', 'Phường Hàng Buồm',
  'Phường Hàng Đào', 'Phường Hàng Bồ', 'Phường Hàng Bạc', 'Phường Hàng Gai', 'Phường Chương Dương',
  'Phường Hàng Trống', 'Phường Cửa Nam', 'Phường Hàng Bông', 'Phường Tràng Tiền', 'Phường Trần Hưng Đạo',
];

const DISTRICTS: Record<string, string[]> = {
  'Ba Đình': ['Phường Phúc Xá', 'Phường Trúc Bạch', 'Phường Vĩnh Phúc', 'Phường Cống Vị', 'Phường Liễu Giai',
              'Phường Nguyễn Trung Trực', 'Phường Quán Thánh', 'Phường Ngọc Hà', 'Phường Điện Biên', 'Phường Đội Cấn',
              'Phường Ba Đình', 'Phường Kim Mã', 'Phường Giảng Võ', 'Phường Thành Công'],
  'Hoàn Kiếm': ['Phường Hàng Buồm', 'Phường Hàng Đào', 'Phường Hàng Bồ', 'Phường Hàng Bạc', 'Phường Hàng Gai',
                'Phường Chương Dương', 'Phường Hàng Trống', 'Phường Cửa Nam', 'Phường Hàng Bông', 'Phường Tràng Tiền',
                'Phường Trần Hưng Đạo'],
};

const getRandomWard = (): { ward: string; district: string } => {
  const ward = HANOI_WARDS[Math.floor(Math.random() * HANOI_WARDS.length)];
  for (const [district, wards] of Object.entries(DISTRICTS)) {
    if (wards.includes(ward)) return { ward, district };
  }
  return { ward, district: 'Hà Nội' };
};

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const metrics: CityMetrics = body.metrics || {};
    
    if (!GEMINI_API_KEY) {
      return NextResponse.json(
        { success: false, error: 'Gemini API key not configured' },
        { status: 500 }
      );
    }

    const genAI = new GoogleGenerativeAI(GEMINI_API_KEY);
    const model = genAI.getGenerativeModel({ model: 'gemini-2.0-flash-exp' });

    const prompt = `
Bạn là hệ thống AI giám sát đô thị thông minh CityLens cho thành phố Hà Nội.
Dựa trên dữ liệu thời gian thực sau đây, hãy phân tích và tạo ra các cảnh báo thông minh cho người dân.

**DỮ LIỆU HIỆN TẠI:**
- Chỉ số AQI (Chất lượng không khí): ${metrics.aqi || 'Không có dữ liệu'}
- Nhiệt độ: ${metrics.temperature || 'Không có dữ liệu'}°C
- Độ ẩm: ${metrics.humidity || 'Không có dữ liệu'}%
- Tốc độ giao thông trung bình: ${metrics.traffic_speed || 'Không có dữ liệu'} km/h
- Mức độ tắc nghẽn: ${metrics.congestion_level || 'Không có dữ liệu'}%
- Sự cố dân sự đang chờ xử lý: ${metrics.pending_issues || 'Không có dữ liệu'}
- Tỷ lệ lấp đầy bãi đỗ xe: ${metrics.parking_occupancy || 'Không có dữ liệu'}%

**YÊU CẦU:**
Tạo 3-5 cảnh báo dựa trên phân tích thông minh. Mỗi cảnh báo cần:
1. Xác định loại (environment/traffic/civic/parking/health/safety)
2. Đánh giá mức độ nghiêm trọng (critical/warning/info)
3. Tiêu đề ngắn gọn (tiếng Việt)
4. Mô tả chi tiết tình huống (tiếng Việt)
5. Khuyến nghị hành động cụ thể cho người dân (tiếng Việt)
6. Đánh giá tác động (tiếng Việt)
7. Ước tính số người bị ảnh hưởng (tiếng Việt)

Trả về JSON array:
[
  {
    "type": "environment|traffic|civic|parking|health|safety",
    "severity": "critical|warning|info",
    "title": "Tiêu đề tiếng Việt",
    "description": "Mô tả chi tiết tiếng Việt",
    "recommendation": "Khuyến nghị cho người dân",
    "impact": "Đánh giá tác động",
    "affectedPopulation": "Ước tính số người ảnh hưởng"
  }
]

Lưu ý: Nếu các chỉ số bình thường, vẫn tạo 1-2 cảnh báo mức "info" để thông báo tình trạng tốt.
`;

    const result = await model.generateContent(prompt);
    const response = result.response.text();
    
    // Parse JSON from response
    const jsonMatch = response.match(/\[[\s\S]*\]/);
    if (!jsonMatch) {
      throw new Error('Invalid response format from Gemini');
    }

    const alertsData = JSON.parse(jsonMatch[0]);
    
    // Add metadata to each alert
    const alerts: GeneratedAlert[] = alertsData.map((alert: any, index: number) => {
      const { ward, district } = getRandomWard();
      return {
        id: `gemini-alert-${Date.now()}-${index}`,
        type: alert.type || 'environment',
        severity: alert.severity || 'info',
        title: alert.title || 'Cảnh báo hệ thống',
        description: alert.description || 'Đang phân tích...',
        ward,
        district,
        recommendation: alert.recommendation || 'Đang cập nhật khuyến nghị...',
        impact: alert.impact || 'Đang đánh giá tác động...',
        affectedPopulation: alert.affectedPopulation || 'Đang ước tính...',
        timestamp: new Date().toISOString(),
      };
    });

    return NextResponse.json({
      success: true,
      data: alerts,
      generated_at: new Date().toISOString(),
      model: 'gemini-2.0-flash-exp',
    });
  } catch (error) {
    console.error('Smart Alerts API error:', error);
    return NextResponse.json(
      { 
        success: false, 
        error: error instanceof Error ? error.message : 'Unknown error',
        data: [],
      },
      { status: 500 }
    );
  }
}

export async function GET() {
  return NextResponse.json({
    success: true,
    message: 'Smart Alerts API - Use POST to generate alerts with city metrics',
    endpoints: {
      'POST /api/smart-alerts': 'Generate AI-powered alerts based on city metrics',
    },
  });
}
