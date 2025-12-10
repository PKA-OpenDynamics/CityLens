// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

/**
 * Gemini AI Service
 * Sử dụng Gemini 2.5 để phân tích dữ liệu thông minh
 */

import { GoogleGenerativeAI } from '@google/generative-ai';

const GEMINI_API_KEY = process.env.GEMINI_API_KEY || '';

let genAI: GoogleGenerativeAI | null = null;

// Initialize Gemini AI
const initGemini = () => {
  if (!genAI && GEMINI_API_KEY) {
    genAI = new GoogleGenerativeAI(GEMINI_API_KEY);
  }
  return genAI;
};

export interface CityHealthAnalysis {
  overall_assessment: string;
  environmental_insights: string;
  traffic_insights: string;
  civic_insights: string;
  parking_insights: string;
  key_recommendations: string[];
  priority_actions: string[];
}

export interface DataInsightAnalysis {
  correlation_analysis: string;
  district_comparison: string;
  temporal_patterns: string;
  predictive_insights: string;
  actionable_recommendations: string[];
}

export interface AlertAnalysis {
  severity_assessment: string;
  impact_prediction: string;
  recommended_actions: string[];
  resource_allocation: string;
  timeline_estimate: string;
}

class GeminiService {
  /**
   * Phân tích sức khỏe đô thị tổng thể
   */
  async analyzeCityHealth(data: {
    overall_score: number;
    environmental: any;
    traffic: any;
    civic: any;
    parking: any;
  }): Promise<CityHealthAnalysis> {
    try {
      const ai = initGemini();
      if (!ai) {
        throw new Error('Gemini API key not configured');
      }

      const model = ai.getGenerativeModel({ model: 'gemini-2.0-flash-exp' });

      const prompt = `
Bạn là chuyên gia phân tích đô thị thông minh. Phân tích dữ liệu sau và đưa ra nhận định chuyên sâu bằng tiếng Việt:

**ĐIỂM SỨC KHỎE ĐÔ THỊ TỔNG THỂ: ${data.overall_score}/100**

**MÔI TRƯỜNG:**
- Điểm: ${data.environmental.score}/100
- AQI: ${data.environmental.aqi_value} (${data.environmental.aqi_status})
- Nhiệt độ: ${data.environmental.temperature}°C
- Độ ẩm: ${data.environmental.humidity}%

**GIAO THÔNG:**
- Điểm: ${data.traffic.score}/100
- Mức độ tắc nghẽn: ${data.traffic.congestion_level}
- Tốc độ trung bình: ${data.traffic.average_speed} km/h

**PHẢN HỒI SỰ CỐ DÂN SỰ:**
- Điểm: ${data.civic.score}/100
- Sự cố đang chờ: ${data.civic.pending_issues}
- Tỷ lệ giải quyết: ${data.civic.resolution_rate}%
- Thời gian xử lý TB: ${data.civic.avg_resolution_time} ngày

**BÃI ĐỖ XE:**
- Điểm: ${data.parking.score}/100
- Tỷ lệ lấp đầy: ${data.parking.occupancy_rate}%
- Chỗ còn trống: ${data.parking.available_spots}

Hãy đưa ra:
1. **Đánh giá tổng thể**: Nhận định về tình trạng chung của đô thị (2-3 câu)
2. **Phân tích môi trường**: Nhận định về chất lượng không khí và thời tiết (2 câu)
3. **Phân tích giao thông**: Đánh giá hiệu suất giao thông (2 câu)
4. **Phân tích phản hồi dân sự**: Đánh giá khả năng xử lý sự cố (2 câu)
5. **Phân tích bãi đỗ xe**: Đánh giá tình trạng đỗ xe (2 câu)
6. **Khuyến nghị chính**: 3-4 khuyến nghị quan trọng nhất (ngắn gọn, dạng bullet point)
7. **Hành động ưu tiên**: 3 hành động cần làm ngay (ngắn gọn, dạng bullet point)

Trả về JSON format:
{
  "overall_assessment": "string",
  "environmental_insights": "string",
  "traffic_insights": "string",
  "civic_insights": "string",
  "parking_insights": "string",
  "key_recommendations": ["string", "string", "string"],
  "priority_actions": ["string", "string", "string"]
}
`;

      const result = await model.generateContent(prompt);
      const response = result.response.text();
      
      // Parse JSON from response
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }

      throw new Error('Invalid response format');
    } catch (error) {
      console.error('Gemini analysis error:', error);
      // Fallback response
      return {
        overall_assessment: 'Không thể phân tích dữ liệu lúc này. Vui lòng thử lại sau.',
        environmental_insights: 'Dữ liệu môi trường đang được thu thập.',
        traffic_insights: 'Dữ liệu giao thông đang được phân tích.',
        civic_insights: 'Dữ liệu sự cố dân sự đang được xử lý.',
        parking_insights: 'Dữ liệu bãi đỗ xe đang được cập nhật.',
        key_recommendations: ['Tiếp tục giám sát hệ thống', 'Thu thập thêm dữ liệu', 'Cải thiện cơ sở hạ tầng'],
        priority_actions: ['Kiểm tra kết nối API', 'Xác minh dữ liệu', 'Cập nhật cảm biến'],
      };
    }
  }

  /**
   * Phân tích correlation và patterns trong dữ liệu
   */
  async analyzeDataInsights(data: {
    weather_aqi_correlation: any[];
    district_performance: any[];
    temporal_patterns: any[];
    predictive_trends: any[];
  }): Promise<DataInsightAnalysis> {
    try {
      const ai = initGemini();
      if (!ai) {
        throw new Error('Gemini API key not configured');
      }

      const model = ai.getGenerativeModel({ model: 'gemini-2.0-flash-exp' });

      // Calculate some statistics
      const avgAqi = data.weather_aqi_correlation.reduce((sum, d) => sum + d.aqi, 0) / data.weather_aqi_correlation.length;
      const avgTemp = data.weather_aqi_correlation.reduce((sum, d) => sum + d.temperature, 0) / data.weather_aqi_correlation.length;
      const bestDistrict = data.district_performance.reduce((best, d) => 
        d.aqi_score > best.aqi_score ? d : best
      );
      const worstDistrict = data.district_performance.reduce((worst, d) => 
        d.aqi_score < worst.aqi_score ? d : worst
      );

      const prompt = `
Bạn là nhà khoa học dữ liệu chuyên về đô thị thông minh. Phân tích các pattern và correlation sau bằng tiếng Việt:

**DỮ LIỆU TỔNG HỢP:**
- AQI trung bình 24h: ${avgAqi.toFixed(1)}
- Nhiệt độ trung bình: ${avgTemp.toFixed(1)}°C
- Quận tốt nhất: ${bestDistrict.district} (AQI score: ${bestDistrict.aqi_score.toFixed(1)})
- Quận cần cải thiện: ${worstDistrict.district} (AQI score: ${worstDistrict.aqi_score.toFixed(1)})
- Số quận theo dõi: ${data.district_performance.length}
- Dữ liệu temporal: ${data.temporal_patterns.length} điểm thời gian

**YÊU CẦU PHÂN TÍCH:**
1. **Phân tích correlation**: Mối quan hệ giữa thời tiết và chất lượng không khí (2-3 câu)
2. **So sánh quận**: Nhận định về sự khác biệt giữa các quận và nguyên nhân (2-3 câu)
3. **Patterns theo thời gian**: Phát hiện các mẫu hoạt động trong ngày (2-3 câu)
4. **Dự đoán và xu hướng**: Nhận định về xu hướng tương lai dựa trên dữ liệu (2-3 câu)
5. **Khuyến nghị hành động**: 4-5 khuyến nghị cụ thể dựa trên phân tích

Trả về JSON format:
{
  "correlation_analysis": "string",
  "district_comparison": "string",
  "temporal_patterns": "string",
  "predictive_insights": "string",
  "actionable_recommendations": ["string", "string", "string", "string"]
}
`;

      const result = await model.generateContent(prompt);
      const response = result.response.text();
      
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }

      throw new Error('Invalid response format');
    } catch (error) {
      console.error('Gemini insights analysis error:', error);
      return {
        correlation_analysis: 'Đang phân tích mối quan hệ giữa các biến số.',
        district_comparison: 'Đang so sánh hiệu suất giữa các quận.',
        temporal_patterns: 'Đang phát hiện các mẫu hoạt động theo thời gian.',
        predictive_insights: 'Đang xây dựng mô hình dự đoán.',
        actionable_recommendations: ['Thu thập thêm dữ liệu', 'Cải thiện độ chính xác', 'Mở rộng phạm vi giám sát', 'Tối ưu hóa hệ thống'],
      };
    }
  }

  /**
   * Phân tích cảnh báo và đưa ra khuyến nghị
   */
  async analyzeAlert(alert: {
    type: string;
    severity: string;
    title: string;
    description: string;
    current_data: any;
  }): Promise<AlertAnalysis> {
    try {
      const ai = initGemini();
      if (!ai) {
        throw new Error('Gemini API key not configured');
      }

      const model = ai.getGenerativeModel({ model: 'gemini-2.0-flash-exp' });

      const prompt = `
Bạn là chuyên gia quản lý khẩn cấp đô thị. Phân tích cảnh báo sau và đưa ra khuyến nghị bằng tiếng Việt:

**CẢNH BÁO:**
- Loại: ${alert.type}
- Mức độ: ${alert.severity}
- Tiêu đề: ${alert.title}
- Mô tả: ${alert.description}

**DỮ LIỆU HIỆN TẠI:**
${JSON.stringify(alert.current_data, null, 2)}

Hãy đưa ra:
1. **Đánh giá mức độ nghiêm trọng**: Phân tích chi tiết về mức độ ảnh hưởng (2-3 câu)
2. **Dự đoán tác động**: Những hậu quả có thể xảy ra nếu không xử lý (2-3 câu)
3. **Hành động khuyến nghị**: 3-4 hành động cụ thể cần thực hiện ngay (bullet points)
4. **Phân bổ nguồn lực**: Nguồn lực và nhân sự cần thiết (1-2 câu)
5. **Ước tính thời gian**: Thời gian dự kiến để giải quyết (1 câu)

Trả về JSON format:
{
  "severity_assessment": "string",
  "impact_prediction": "string",
  "recommended_actions": ["string", "string", "string"],
  "resource_allocation": "string",
  "timeline_estimate": "string"
}
`;

      const result = await model.generateContent(prompt);
      const response = result.response.text();
      
      const jsonMatch = response.match(/\{[\s\S]*\}/);
      if (jsonMatch) {
        return JSON.parse(jsonMatch[0]);
      }

      throw new Error('Invalid response format');
    } catch (error) {
      console.error('Gemini alert analysis error:', error);
      return {
        severity_assessment: 'Đang đánh giá mức độ nghiêm trọng của cảnh báo.',
        impact_prediction: 'Đang phân tích tác động tiềm tàng.',
        recommended_actions: ['Giám sát tình hình', 'Chuẩn bị kế hoạch ứng phó', 'Thông báo cho các bên liên quan'],
        resource_allocation: 'Đang đánh giá nguồn lực cần thiết.',
        timeline_estimate: 'Đang ước tính thời gian xử lý.',
      };
    }
  }
}

export const geminiService = new GeminiService();
export default geminiService;
