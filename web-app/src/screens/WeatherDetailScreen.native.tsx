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

interface WeatherData {
  temperature: number;
  description: string;
  humidity: number;
  windSpeed: number;
  pressure: number;
  visibility: number;
  uvIndex: number;
  forecast: Array<{
    time: string;
    icon: keyof typeof MaterialIcons.glyphMap;
    temp: string;
    description: string;
  }>;
}

const WeatherDetailScreen: React.FC = () => {
  const navigation = useNavigation<any>();
  const route = useRoute();
  const [loading, setLoading] = useState(true);
  const [weatherData, setWeatherData] = useState<WeatherData | null>(null);

  useEffect(() => {
    loadWeatherData();
  }, []);

  const loadWeatherData = async () => {
    // TODO: Implement actual API call
    setLoading(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock data
      setWeatherData({
        temperature: 28,
        description: 'Có mây, có thể mưa',
        humidity: 75,
        windSpeed: 12,
        pressure: 1013,
        visibility: 10,
        uvIndex: 6,
        forecast: [
          { time: '15:00', icon: 'wb-sunny', temp: '29°', description: 'Nắng' },
          { time: '18:00', icon: 'wb-cloudy', temp: '27°', description: 'Có mây' },
          { time: '21:00', icon: 'wb-cloudy', temp: '25°', description: 'Có mây' },
          { time: '00:00', icon: 'wb-cloudy', temp: '24°', description: 'Có mây' },
          { time: '03:00', icon: 'wb-cloudy', temp: '23°', description: 'Có mây' },
          { time: '06:00', icon: 'wb-sunny', temp: '24°', description: 'Nắng' },
        ],
      });
    } catch (error) {
      console.error('Error loading weather data:', error);
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

  if (!weatherData) {
    return (
      <SafeAreaView style={styles.safeArea}>
        <View style={styles.errorContainer}>
          <Text style={styles.errorText}>Không thể tải dữ liệu thời tiết</Text>
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
        <Text style={styles.headerTitle}>Chi tiết thời tiết</Text>
      </LinearGradient>

      <ScrollView style={styles.content} contentContainerStyle={styles.contentContainer}>
        {/* Main Temperature Card */}
        <View style={styles.mainCard}>
          <View style={styles.temperatureRow}>
            <Text style={styles.temperatureText}>{weatherData.temperature}°C</Text>
            <MaterialIcons name="wb-cloudy" size={64} color="#20A957" />
          </View>
          <Text style={styles.descriptionText}>{weatherData.description}</Text>
        </View>

        {/* Stats Grid */}
        <View style={styles.statsGrid}>
          <View style={styles.statCard}>
            <MaterialIcons name="opacity" size={24} color="#20A957" />
            <Text style={styles.statValue}>{weatherData.humidity}%</Text>
            <Text style={styles.statLabel}>Độ ẩm</Text>
          </View>
          <View style={styles.statCard}>
            <MaterialIcons name="air" size={24} color="#20A957" />
            <Text style={styles.statValue}>{weatherData.windSpeed} km/h</Text>
            <Text style={styles.statLabel}>Tốc độ gió</Text>
          </View>
          <View style={styles.statCard}>
            <MaterialIcons name="speed" size={24} color="#20A957" />
            <Text style={styles.statValue}>{weatherData.pressure} hPa</Text>
            <Text style={styles.statLabel}>Áp suất</Text>
          </View>
          <View style={styles.statCard}>
            <MaterialIcons name="visibility" size={24} color="#20A957" />
            <Text style={styles.statValue}>{weatherData.visibility} km</Text>
            <Text style={styles.statLabel}>Tầm nhìn</Text>
          </View>
          <View style={styles.statCard}>
            <MaterialIcons name="wb-sunny" size={24} color="#20A957" />
            <Text style={styles.statValue}>{weatherData.uvIndex}</Text>
            <Text style={styles.statLabel}>Chỉ số UV</Text>
          </View>
        </View>

        {/* Forecast Section */}
        <View style={styles.forecastSection}>
          <Text style={styles.sectionTitle}>Dự báo theo giờ</Text>
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={styles.forecastScroll}>
            {weatherData.forecast.map((item, index) => (
              <View key={index} style={styles.forecastItem}>
                <Text style={styles.forecastTime}>{item.time}</Text>
                <MaterialIcons name={item.icon} size={32} color="#20A957" />
                <Text style={styles.forecastTemp}>{item.temp}</Text>
                <Text style={styles.forecastDesc}>{item.description}</Text>
              </View>
            ))}
          </ScrollView>
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
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  temperatureRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  temperatureText: {
    fontSize: 64,
    fontWeight: '700',
    color: '#111827',
    marginRight: 16,
  },
  descriptionText: {
    fontSize: 18,
    color: '#6B7280',
    textAlign: 'center',
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 16,
  },
  statCard: {
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
  statValue: {
    fontSize: 20,
    fontWeight: '700',
    color: '#111827',
    marginTop: 8,
    marginBottom: 4,
  },
  statLabel: {
    fontSize: 12,
    color: '#6B7280',
  },
  forecastSection: {
    marginTop: 8,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 12,
  },
  forecastScroll: {
    marginHorizontal: -16,
    paddingHorizontal: 16,
  },
  forecastItem: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginRight: 12,
    minWidth: 100,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  forecastTime: {
    fontSize: 14,
    fontWeight: '600',
    color: '#6B7280',
    marginBottom: 8,
  },
  forecastTemp: {
    fontSize: 18,
    fontWeight: '700',
    color: '#111827',
    marginTop: 8,
    marginBottom: 4,
  },
  forecastDesc: {
    fontSize: 12,
    color: '#6B7280',
    textAlign: 'center',
  },
});

export default WeatherDetailScreen;


