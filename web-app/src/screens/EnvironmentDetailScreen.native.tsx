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
  Alert,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialIcons } from '@expo/vector-icons';
import { useNavigation, useRoute } from '@react-navigation/native';
import { weatherService, RealtimeWeatherResponse } from '../services/weather';

interface RouteParams {
  locationId?: string;
  userLocation?: { lat: number; lon: number };
}

const EnvironmentDetailScreen: React.FC = () => {
  const navigation = useNavigation<any>();
  const route = useRoute();
  const params = route.params as RouteParams;
  
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'weather' | 'air'>('weather');
  const [realtimeData, setRealtimeData] = useState<RealtimeWeatherResponse | null>(null);
  const [locationName, setLocationName] = useState<string>('');

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      let data: RealtimeWeatherResponse | null = null;

      // Try to get data by locationId first
      if (params?.locationId) {
        try {
          data = await weatherService.getRealtimeWeather(params.locationId);
          setLocationName(data.location_name || '');
        } catch (error) {
          console.warn('Error loading by locationId, trying nearby:', error);
        }
      }

      // Fallback to nearby if locationId fails or not provided
      if (!data && params?.userLocation) {
        try {
          const nearbyData = await weatherService.getNearbyRealtime(
            params.userLocation.lat,
            params.userLocation.lon,
            10000,
            1
          );
          if (nearbyData && nearbyData.length > 0) {
            data = nearbyData[0];
            setLocationName(data.location_name || '');
          }
        } catch (error) {
          console.error('Error loading nearby realtime:', error);
        }
      }

      // If still no data, use default location (Hanoi)
      if (!data) {
        const defaultLocation = { lat: 21.0285, lon: 105.8542 };
        try {
          const nearbyData = await weatherService.getNearbyRealtime(
            defaultLocation.lat,
            defaultLocation.lon,
            10000,
            1
          );
          if (nearbyData && nearbyData.length > 0) {
            data = nearbyData[0];
            setLocationName(data.location_name || 'Hà Nội');
          }
        } catch (error) {
          console.error('Error loading default location data:', error);
          Alert.alert('Lỗi', 'Không thể tải dữ liệu môi trường. Vui lòng thử lại sau.');
        }
      }

      setRealtimeData(data);
    } catch (error) {
      console.error('Error loading environment data:', error);
      Alert.alert('Lỗi', 'Không thể tải dữ liệu môi trường. Vui lòng thử lại sau.');
    } finally {
      setLoading(false);
    }
  };

  const getWeatherIcon = (condition?: string): keyof typeof MaterialIcons.glyphMap => {
    if (!condition) return 'wb-cloudy';
    const lower = condition.toLowerCase();
    if (lower.includes('nắng') || lower.includes('sunny')) return 'wb-sunny';
    if (lower.includes('mưa') || lower.includes('rain')) return 'grain';
    if (lower.includes('mây') || lower.includes('cloud')) return 'wb-cloudy';
    return 'wb-cloudy';
  };

  const getAQIColor = (aqi: number): string => {
    if (aqi <= 50) return '#10B981';
    if (aqi <= 100) return '#F59E0B';
    if (aqi <= 150) return '#F97316';
    if (aqi <= 200) return '#EF4444';
    return '#7C2D12';
  };

  const getAQILevel = (aqi: number): string => {
    if (aqi <= 50) return 'Tốt';
    if (aqi <= 100) return 'Trung bình';
    if (aqi <= 150) return 'Kém';
    if (aqi <= 200) return 'Xấu';
    return 'Rất xấu';
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
        <Text style={styles.headerTitle}>Môi trường</Text>
        {locationName ? (
          <Text style={styles.headerSubtitle}>{locationName}</Text>
        ) : null}
      </LinearGradient>

      {/* Tab Selector */}
      <View style={styles.tabContainer}>
        <TouchableOpacity
          style={[styles.tab, activeTab === 'weather' && styles.tabActive]}
          onPress={() => setActiveTab('weather')}
        >
          <MaterialIcons
            name="wb-cloudy"
            size={20}
            color={activeTab === 'weather' ? '#20A957' : '#9CA3AF'}
          />
          <Text
            style={[
              styles.tabText,
              activeTab === 'weather' && styles.tabTextActive,
            ]}
          >
            Thời tiết
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tab, activeTab === 'air' && styles.tabActive]}
          onPress={() => setActiveTab('air')}
        >
          <MaterialIcons
            name="air"
            size={20}
            color={activeTab === 'air' ? '#20A957' : '#9CA3AF'}
          />
          <Text
            style={[
              styles.tabText,
              activeTab === 'air' && styles.tabTextActive,
            ]}
          >
            Chất lượng không khí
          </Text>
        </TouchableOpacity>
      </View>

      <ScrollView style={styles.content} contentContainerStyle={styles.contentContainer}>
        {activeTab === 'weather' ? (
          // Weather Tab
          <View>
            <View style={styles.card}>
              <View style={styles.cardHeader}>
                <MaterialIcons
                  name={getWeatherIcon(realtimeData?.weather?.condition)}
                  size={32}
                  color="#20A957"
                />
                <View style={styles.cardHeaderText}>
                  <Text style={styles.cardTitle}>Thời tiết hiện tại</Text>
                  <Text style={styles.cardSubtitle}>
                    {realtimeData?.weather?.condition || 'N/A'}
                  </Text>
                </View>
              </View>

              <View style={styles.temperatureContainer}>
                <Text style={styles.temperature}>
                  {realtimeData?.weather?.temp ? `${Math.round(realtimeData.weather.temp)}°C` : '--°C'}
                </Text>
                {realtimeData?.weather?.feels_like && (
                  <Text style={styles.feelsLike}>
                    Cảm giác như {Math.round(realtimeData.weather.feels_like)}°C
                  </Text>
                )}
              </View>

              <View style={styles.detailsGrid}>
                <View style={styles.detailItem}>
                  <MaterialIcons name="water-drop" size={20} color="#20A957" />
                  <Text style={styles.detailLabel}>Độ ẩm</Text>
                  <Text style={styles.detailValue}>
                    {realtimeData?.weather?.humidity || '--'}%
                  </Text>
                </View>

                <View style={styles.detailItem}>
                  <MaterialIcons name="air" size={20} color="#20A957" />
                  <Text style={styles.detailLabel}>Gió</Text>
                  <Text style={styles.detailValue}>
                    {realtimeData?.weather?.wind_speed ? `${realtimeData.weather.wind_speed} m/s` : '--'}
                  </Text>
                </View>

                <View style={styles.detailItem}>
                  <MaterialIcons name="speed" size={20} color="#20A957" />
                  <Text style={styles.detailLabel}>Áp suất</Text>
                  <Text style={styles.detailValue}>
                    {realtimeData?.weather?.pressure || '--'} hPa
                  </Text>
                </View>

                {realtimeData?.weather?.visibility && (
                  <View style={styles.detailItem}>
                    <MaterialIcons name="visibility" size={20} color="#20A957" />
                    <Text style={styles.detailLabel}>Tầm nhìn</Text>
                    <Text style={styles.detailValue}>
                      {realtimeData.weather.visibility / 1000} km
                    </Text>
                  </View>
                )}

                {realtimeData?.weather?.clouds !== undefined && (
                  <View style={styles.detailItem}>
                    <MaterialIcons name="wb-cloudy" size={20} color="#20A957" />
                    <Text style={styles.detailLabel}>Mây</Text>
                    <Text style={styles.detailValue}>
                      {realtimeData.weather.clouds}%
                    </Text>
                  </View>
                )}

                {realtimeData?.weather?.rain_1h !== undefined && (
                  <View style={styles.detailItem}>
                    <MaterialIcons name="grain" size={20} color="#20A957" />
                    <Text style={styles.detailLabel}>Mưa (1h)</Text>
                    <Text style={styles.detailValue}>
                      {realtimeData.weather.rain_1h} mm
                    </Text>
                  </View>
                )}
              </View>

              {realtimeData?.timestamp && (
                <Text style={styles.dataTimestamp}>
                  Cập nhật: {new Date(realtimeData.timestamp).toLocaleString('vi-VN')}
                </Text>
              )}
            </View>
          </View>
        ) : (
          // Air Quality Tab
          <View>
            <View style={styles.card}>
              <View style={styles.cardHeader}>
                <MaterialIcons
                  name="air"
                  size={32}
                  color={getAQIColor(realtimeData?.air_quality?.aqi || 0)}
                />
                <View style={styles.cardHeaderText}>
                  <Text style={styles.cardTitle}>Chất lượng không khí</Text>
                  <Text style={[styles.cardSubtitle, { color: getAQIColor(realtimeData?.air_quality?.aqi || 0) }]}>
                    {getAQILevel(realtimeData?.air_quality?.aqi || 0)}
                  </Text>
                </View>
              </View>

              <View style={styles.aqiContainer}>
                <Text style={[styles.aqiValue, { color: getAQIColor(realtimeData?.air_quality?.aqi || 0) }]}>
                  {realtimeData?.air_quality?.aqi || '--'}
                </Text>
                <Text style={styles.aqiLabel}>AQI</Text>
              </View>

              <View style={styles.detailsGrid}>
                {realtimeData?.air_quality?.pm2_5 !== undefined && (
                  <View style={styles.detailItem}>
                    <MaterialIcons name="filter-alt" size={20} color="#20A957" />
                    <Text style={styles.detailLabel}>PM2.5</Text>
                    <Text style={styles.detailValue}>
                      {realtimeData.air_quality.pm2_5.toFixed(1)} µg/m³
                    </Text>
                  </View>
                )}

                {realtimeData?.air_quality?.pm10 !== undefined && (
                  <View style={styles.detailItem}>
                    <MaterialIcons name="filter-alt" size={20} color="#20A957" />
                    <Text style={styles.detailLabel}>PM10</Text>
                    <Text style={styles.detailValue}>
                      {realtimeData.air_quality.pm10.toFixed(1)} µg/m³
                    </Text>
                  </View>
                )}

                {realtimeData?.air_quality?.co !== undefined && (
                  <View style={styles.detailItem}>
                    <MaterialIcons name="local-fire-department" size={20} color="#20A957" />
                    <Text style={styles.detailLabel}>CO</Text>
                    <Text style={styles.detailValue}>
                      {realtimeData.air_quality.co.toFixed(1)} µg/m³
                    </Text>
                  </View>
                )}

                {realtimeData?.air_quality?.no2 !== undefined && (
                  <View style={styles.detailItem}>
                    <MaterialIcons name="factory" size={20} color="#20A957" />
                    <Text style={styles.detailLabel}>NO₂</Text>
                    <Text style={styles.detailValue}>
                      {realtimeData.air_quality.no2.toFixed(1)} µg/m³
                    </Text>
                  </View>
                )}

                {realtimeData?.air_quality?.o3 !== undefined && (
                  <View style={styles.detailItem}>
                    <MaterialIcons name="wb-sunny" size={20} color="#20A957" />
                    <Text style={styles.detailLabel}>O₃</Text>
                    <Text style={styles.detailValue}>
                      {realtimeData.air_quality.o3.toFixed(1)} µg/m³
                    </Text>
                  </View>
                )}

                {realtimeData?.air_quality?.so2 !== undefined && (
                  <View style={styles.detailItem}>
                    <MaterialIcons name="factory" size={20} color="#20A957" />
                    <Text style={styles.detailLabel}>SO₂</Text>
                    <Text style={styles.detailValue}>
                      {realtimeData.air_quality.so2.toFixed(1)} µg/m³
                    </Text>
                  </View>
                )}
              </View>

              {realtimeData?.timestamp && (
                <Text style={styles.dataTimestamp}>
                  Cập nhật: {new Date(realtimeData.timestamp).toLocaleString('vi-VN')}
                </Text>
              )}
            </View>
          </View>
        )}
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
  headerSubtitle: {
    fontSize: 14,
    color: '#FFFFFF',
    opacity: 0.9,
    marginTop: 4,
  },
  tabContainer: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  tab: {
    flex: 1,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    borderRadius: 8,
    marginHorizontal: 4,
  },
  tabActive: {
    backgroundColor: '#F0FDF4',
  },
  tabText: {
    marginLeft: 8,
    fontSize: 14,
    color: '#9CA3AF',
    fontWeight: '500',
  },
  tabTextActive: {
    color: '#20A957',
    fontWeight: '600',
  },
  content: {
    flex: 1,
  },
  contentContainer: {
    padding: 16,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 20,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  cardHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 20,
  },
  cardHeaderText: {
    marginLeft: 12,
    flex: 1,
  },
  cardTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
  },
  cardSubtitle: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 4,
  },
  temperatureContainer: {
    alignItems: 'center',
    marginVertical: 20,
  },
  temperature: {
    fontSize: 64,
    fontWeight: '700',
    color: '#20A957',
  },
  feelsLike: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 8,
  },
  aqiContainer: {
    alignItems: 'center',
    marginVertical: 20,
  },
  aqiValue: {
    fontSize: 64,
    fontWeight: '700',
  },
  aqiLabel: {
    fontSize: 16,
    color: '#6B7280',
    marginTop: 8,
  },
  detailsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    marginTop: 20,
  },
  detailItem: {
    width: '33.33%',
    alignItems: 'center',
    paddingVertical: 12,
  },
  detailLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 8,
    marginBottom: 4,
  },
  detailValue: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  dataTimestamp: {
    fontSize: 12,
    color: '#9CA3AF',
    marginTop: 16,
    textAlign: 'center',
    fontStyle: 'italic',
  },
});

export default EnvironmentDetailScreen;

