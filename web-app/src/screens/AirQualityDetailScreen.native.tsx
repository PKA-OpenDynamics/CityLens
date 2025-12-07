// Copyright (c) 2025 CityLens Contributors

// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialIcons } from '@expo/vector-icons';
import { useNavigation, useRoute } from '@react-navigation/native';

interface AirQualityData {
  aqi: number;
  level: string;
  levelColor: string;
  description: string;
  pollutants: {
    pm25: number;
    pm10: number;
    o3: number;
    no2: number;
    co: number;
    so2: number;
  };
  healthAdvice: string;
  recommendations: string[];
}

const AirQualityDetailScreen: React.FC = () => {
  const navigation = useNavigation<any>();
  const route = useRoute();
  const [loading, setLoading] = useState(true);
  const [aqiData, setAqiData] = useState<AirQualityData | null>(null);

  useEffect(() => {
    loadAQIData();
  }, []);

  const getAQILevel = (aqi: number): { level: string; color: string; description: string } => {
    if (aqi <= 50) {
      return { level: 'Tốt', color: '#10B981', description: 'Chất lượng không khí tốt, phù hợp cho mọi hoạt động ngoài trời.' };
    } else if (aqi <= 100) {
      return { level: 'Trung bình', color: '#F59E0B', description: 'Chất lượng không khí ở mức chấp nhận được.' };
    } else if (aqi <= 150) {
      return { level: 'Kém', color: '#F97316', description: 'Nhóm nhạy cảm có thể gặp vấn đề về sức khỏe.' };
    } else if (aqi <= 200) {
      return { level: 'Xấu', color: '#EF4444', description: 'Mọi người có thể bắt đầu gặp vấn đề về sức khỏe.' };
    } else if (aqi <= 300) {
      return { level: 'Rất xấu', color: '#991B1B', description: 'Cảnh báo sức khỏe: mọi người có thể gặp vấn đề nghiêm trọng.' };
    } else {
      return { level: 'Nguy hiểm', color: '#7C2D12', description: 'Cảnh báo khẩn cấp: toàn bộ dân số có thể bị ảnh hưởng.' };
    }
  };

  const loadAQIData = async () => {
    // TODO: Implement actual API call
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock data
      const aqi = 85;
      const levelInfo = getAQILevel(aqi);
      
      setAqiData({
        aqi,
        level: levelInfo.level,
        levelColor: levelInfo.color,
        description: levelInfo.description,
        pollutants: {
          pm25: 35,
          pm10: 55,
          o3: 120,
          no2: 45,
          co: 1.2,
          so2: 15,
        },
        healthAdvice: 'Chất lượng không khí ở mức chấp nhận được. Nhóm nhạy cảm nên hạn chế hoạt động ngoài trời kéo dài.',
        recommendations: [
          'Đóng cửa sổ khi không khí bên ngoài ô nhiễm',
          'Sử dụng máy lọc không khí trong nhà',
          'Hạn chế tập thể dục ngoài trời vào giờ cao điểm',
          'Đeo khẩu trang khi ra ngoài',
        ],
      });
    } catch (error) {
      console.error('Error loading AQI data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.loadingContainer}>
          <ActivityIndicator size="large" color="#20A957" />
        </View>
      </SafeAreaView>
    );
  }

  if (!aqiData) {
    return (
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>Không thể tải dữ liệu chất lượng không khí</Text>
        </View>
      </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.safeArea}>
      <LinearGradient
        colors={['#20A957', '#7BE882']}
        style={styles.header}
      >
        <TouchableOpacity
          onPress={() => navigation.goBack()}
          style={styles.backButton}
        >
          <MaterialIcons name="arrow-back" size={24} color="#FFFFFF" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Chất lượng không khí</Text>
      </LinearGradient>

      <ScrollView style={styles.content} contentContainerStyle={styles.contentContainer}>
        {/* Main AQI Card */}
        <View style={styles.mainCard}>
          <View style={styles.aqiRow}>
            <View style={styles.aqiCircle}>
              <Text style={styles.aqiValue}>{aqiData.aqi}</Text>
              <Text style={styles.aqiLabel}>AQI</Text>
            </View>
            <View style={styles.aqiInfo}>
              <View style={[styles.levelBadge, { backgroundColor: aqiData.levelColor }]}>
                <Text style={styles.levelText}>{aqiData.level}</Text>
              </View>
              <Text style={styles.descriptionText}>{aqiData.description}</Text>
            </View>
          </View>
        </View>

        {/* Pollutants Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Chỉ số các chất ô nhiễm</Text>
          <View style={styles.pollutantsGrid}>
            <View style={styles.pollutantCard}>
              <MaterialIcons name="cloud" size={24} color="#20A957" />
              <Text style={styles.pollutantValue}>{aqiData.pollutants.pm25}</Text>
              <Text style={styles.pollutantLabel}>PM2.5 (μg/m³)</Text>
            </View>
            <View style={styles.pollutantCard}>
              <MaterialIcons name="cloud-queue" size={24} color="#20A957" />
              <Text style={styles.pollutantValue}>{aqiData.pollutants.pm10}</Text>
              <Text style={styles.pollutantLabel}>PM10 (μg/m³)</Text>
            </View>
            <View style={styles.pollutantCard}>
              <MaterialIcons name="wb-sunny" size={24} color="#20A957" />
              <Text style={styles.pollutantValue}>{aqiData.pollutants.o3}</Text>
              <Text style={styles.pollutantLabel}>O₃ (ppb)</Text>
            </View>
            <View style={styles.pollutantCard}>
              <MaterialIcons name="air" size={24} color="#20A957" />
              <Text style={styles.pollutantValue}>{aqiData.pollutants.no2}</Text>
              <Text style={styles.pollutantLabel}>NO₂ (ppb)</Text>
            </View>
            <View style={styles.pollutantCard}>
              <MaterialIcons name="local-fire-department" size={24} color="#20A957" />
              <Text style={styles.pollutantValue}>{aqiData.pollutants.co}</Text>
              <Text style={styles.pollutantLabel}>CO (ppm)</Text>
            </View>
            <View style={styles.pollutantCard}>
              <MaterialIcons name="factory" size={24} color="#20A957" />
              <Text style={styles.pollutantValue}>{aqiData.pollutants.so2}</Text>
              <Text style={styles.pollutantLabel}>SO₂ (ppb)</Text>
            </View>
          </View>
        </View>

        {/* Health Advice */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Lời khuyên sức khỏe</Text>
          <View style={styles.adviceCard}>
            <MaterialIcons name="health-and-safety" size={24} color="#20A957" />
            <Text style={styles.adviceText}>{aqiData.healthAdvice}</Text>
          </View>
        </View>

        {/* Recommendations */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Khuyến nghị</Text>
          {aqiData.recommendations.map((rec, index) => (
            <View key={index} style={styles.recommendationItem}>
              <MaterialIcons name="check-circle" size={20} color="#20A957" />
              <Text style={styles.recommendationText}>{rec}</Text>
            </View>
          ))}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  header: {
    paddingTop: 16,
    paddingBottom: 24,
    paddingHorizontal: 16,
  },
  backButton: {
    alignSelf: 'flex-start',
    marginBottom: 16,
    padding: 8,
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  content: {
    flex: 1,
  },
  contentContainer: {
    padding: 16,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorText: {
    fontSize: 16,
    color: '#6B7280',
  },
  mainCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 24,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  aqiRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  aqiCircle: {
    width: 100,
    height: 100,
    borderRadius: 50,
    backgroundColor: '#F3F4F6',
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 16,
  },
  aqiValue: {
    fontSize: 32,
    fontWeight: '700',
    color: '#111827',
  },
  aqiLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 4,
  },
  aqiInfo: {
    flex: 1,
  },
  levelBadge: {
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 12,
    alignSelf: 'flex-start',
    marginBottom: 8,
  },
  levelText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  descriptionText: {
    fontSize: 14,
    color: '#6B7280',
    lineHeight: 20,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 12,
  },
  pollutantsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  pollutantCard: {
    width: '48%',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  pollutantValue: {
    fontSize: 20,
    fontWeight: '700',
    color: '#111827',
    marginTop: 8,
    marginBottom: 4,
  },
  pollutantLabel: {
    fontSize: 12,
    color: '#6B7280',
    textAlign: 'center',
  },
  adviceCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    flexDirection: 'row',
    alignItems: 'flex-start',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  adviceText: {
    flex: 1,
    fontSize: 14,
    color: '#374151',
    lineHeight: 20,
    marginLeft: 12,
  },
  recommendationItem: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 8,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  recommendationText: {
    flex: 1,
    fontSize: 14,
    color: '#374151',
    lineHeight: 20,
    marginLeft: 12,
  },
});

export default AirQualityDetailScreen;


