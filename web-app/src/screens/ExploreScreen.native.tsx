// Copyright (c) 2025 CityLens Contributors

// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Keyboard,
  Platform,
  TextInput,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialIcons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import Avatar from '../components/Avatar';
import { authService, User } from '../services/auth';
import { weatherService, RealtimeWeatherResponse, ForecastPoint } from '../services/weather';

/**
 * ExploreScreen (native)
 * Được port thủ công từ Flutter `lib/screens/explore_screen.dart`.
 * Tập trung giữ layout và màu sắc chính: header, nhiệt độ, AQI, forecast 3h, nút AI nổi.
 * Dữ liệu được fetch từ MongoDB Atlas qua weather API.
 */

type ForecastItem = {
  time: string;
  icon: keyof typeof MaterialIcons.glyphMap;
  temp: string;
};

type NearbyCard = {
  id: string;
  title: string;
  description: string;
  distance?: string;
  category: 'Giao thông' | 'Môi trường' | 'Phản ánh';
  hasAiButton?: boolean;
};

// Helper function to get weather icon from condition
const getWeatherIcon = (condition?: string): keyof typeof MaterialIcons.glyphMap => {
  if (!condition) return 'wb-cloudy';
  const lower = condition.toLowerCase();
  if (lower.includes('clear') || lower.includes('sun')) return 'wb-sunny';
  if (lower.includes('rain') || lower.includes('drizzle')) return 'grain';
  if (lower.includes('snow')) return 'ac-unit';
  if (lower.includes('cloud')) return 'wb-cloudy';
  if (lower.includes('mist') || lower.includes('fog')) return 'wb-cloudy';
  return 'wb-cloudy';
};

// Helper function to translate weather condition to Vietnamese
const translateCondition = (condition?: string): string => {
  if (!condition) return 'N/A';
  const lower = condition.toLowerCase();
  
  if (lower.includes('clear') || lower.includes('sun')) return 'Trời nắng';
  if (lower.includes('rain') || lower.includes('drizzle')) return 'Có mưa';
  if (lower.includes('snow')) return 'Có tuyết';
  if (lower.includes('cloud')) return 'Có mây';
  if (lower.includes('mist') || lower.includes('fog')) return 'Có sương mù';
  if (lower.includes('thunder')) return 'Có giông';
  if (lower.includes('wind')) return 'Có gió';
  
  return condition; // Return original if no match
};

// Helper function to format time from timestamp
const formatTime = (timestamp: string): string => {
  try {
    const date = new Date(timestamp);
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${hours}:${minutes}`;
  } catch {
    return '';
  }
};

const NEARBY_CARDS: NearbyCard[] = [
  {
    id: '1',
    title: 'Ùn tắc ngã tư Xã Đàn',
    description: 'Lưu lượng xe tăng cao, di chuyển chậm.',
    category: 'Giao thông',
    hasAiButton: true,
  },
  {
    id: '2',
    title: 'Điểm đen rác thải Hồ Yên Sở',
    description: 'Rác tồn đọng nhiều ngày, mùi khó chịu.',
    distance: '1.2km',
    category: 'Môi trường',
  },
  {
    id: '3',
    title: 'Phản ánh lòng đường bị lấn chiếm',
    description: 'Kinh doanh hàng quán trên vỉa hè.',
    distance: '500m',
    category: 'Phản ánh',
  },
];

const ExploreScreen: React.FC = () => {
  const navigation = useNavigation<any>();
  const [showAiButton] = useState(true);
  const [aiBottom] = useState(24);
  const [aiRight] = useState(24);
  const [userName, setUserName] = useState<string | undefined>(undefined);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState<string | null>(null);
  
  // Weather data states
  const [weatherData, setWeatherData] = useState<RealtimeWeatherResponse | null>(null);
  const [forecastData, setForecastData] = useState<ForecastPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [userLocation, setUserLocation] = useState<{ lat: number; lon: number } | null>(null);
  const [locationId, setLocationId] = useState<string | null>(null);

  useEffect(() => {
    loadUserInfo();
    getCurrentLocation();
  }, []);

  useEffect(() => {
    if (userLocation) {
      loadWeatherData();
    }
  }, [userLocation]);

  useEffect(() => {
    if (locationId) {
      loadForecastData();
    }
  }, [locationId]);

  const getCurrentLocation = () => {
    if (Platform.OS === 'web') {
      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            setUserLocation({
              lat: position.coords.latitude,
              lon: position.coords.longitude,
            });
          },
          (error) => {
            // Silently handle geolocation errors (user denied, timeout, etc.)
            // Default to Hoàn Kiếm (Hồ Gươm), Hà Nội if geolocation fails
            if (error.code !== 1) { // Only log if not user denied
              console.warn('Geolocation error:', error.message);
            }
            setUserLocation({ lat: 21.0285, lon: 105.8542 }); // Hoàn Kiếm, Hà Nội
          },
          {
            timeout: 10000,
            maximumAge: 60000,
            enableHighAccuracy: false
          }
        );
      } else {
        // Default to Hoàn Kiếm (Hồ Gươm), Hà Nội if geolocation not available
        setUserLocation({ lat: 21.0285, lon: 105.8542 }); // Hoàn Kiếm, Hà Nội
      }
    } else {
      // For native, you might want to use expo-location
      // For now, default to Hoàn Kiếm (Hồ Gươm), Hà Nội
      setUserLocation({ lat: 21.0285, lon: 105.8542 }); // Hoàn Kiếm, Hà Nội
    }
  };

  const loadUserInfo = async () => {
    try {
      const userData = await authService.getCurrentUser();
      setUserName(userData.full_name || userData.username || 'User');
    } catch (error) {
      // Nếu chưa đăng nhập, dùng giá trị mặc định
      setUserName('User');
    }
  };

  const loadWeatherData = async () => {
    if (!userLocation) return;
    
    try {
      setLoading(true);
      const nearbyData = await weatherService.getNearbyRealtime(
        userLocation.lat,
        userLocation.lon,
        10000,
        1
      );
      
      if (nearbyData && nearbyData.length > 0) {
        const data = nearbyData[0];
        setWeatherData(data);
        setLocationId(data.location_id);
      } else {
        // If no nearby data, use default values
        setWeatherData(null);
      }
    } catch (error) {
      console.error('Error loading weather data:', error);
      setWeatherData(null);
    } finally {
      setLoading(false);
    }
  };

  const loadForecastData = async () => {
    if (!locationId) return;
    
    try {
      const forecast = await weatherService.getForecast(locationId, 5);
      console.log('Forecast data received:', forecast);
      const threeHourForecast = weatherService.getThreeHourForecast(forecast);
      console.log('Three hour forecast:', threeHourForecast);
      setForecastData(threeHourForecast);
    } catch (error) {
      console.error('Error loading forecast data:', error);
      setForecastData([]);
    }
  };

  const handleBackgroundPress = () => {
    Keyboard.dismiss();
  };

  const handleAiPress = () => {
    navigation.navigate('AiAssistant');
  };

  const handleFilterPress = (filter: string) => {
    if (filter === 'environment') {
      // Navigate to environment detail screen (weather + air quality)
      navigation.navigate('EnvironmentDetail', {
        locationId: locationId,
        userLocation: userLocation,
      });
    } else if (filter === 'traffic') {
      // Navigate to Map screen
      navigation.navigate('Map');
    } else if (filter === 'report') {
      // Navigate to Report screen
      navigation.navigate('Report');
    } else {
    setSelectedFilter(selectedFilter === filter ? null : filter);
    }
  };

  const handleCardPress = (card: NearbyCard) => {
    // Navigate to detail or map based on card
    navigation.navigate('Map', { 
      layerType: card.category === 'Giao thông' ? 'traffic' : 
                 card.category === 'Môi trường' ? 'environment' : 'reports' 
    });
  };

  const handleCardAiPress = (card: NearbyCard) => {
    navigation.navigate('AiAssistant', { 
      context: `Thông tin về: ${card.title}. ${card.description}` 
    });
  };

  return (
    <SafeAreaView style={styles.safeArea} onTouchStart={handleBackgroundPress}>
      <View style={styles.root}>
        {/* Nội dung chính */}
        <ScrollView
          style={styles.scroll}
          contentContainerStyle={styles.scrollContent}
          showsVerticalScrollIndicator={false}
        >
          {/* HEADER GRADIENT */}
          <LinearGradient
            colors={['#20A957', '#7BE882']}
            start={{ x: 0.5, y: 1 }}
            end={{ x: 0.5, y: 0 }}
            style={styles.header}
          >
            {/* Top row: title + avatar */}
            <View style={styles.headerTopRow}>
              <View>
                <View style={styles.headerTitleRow}>
                  <MaterialIcons
                    name="explore"
                    size={24}
                    color="#FFFFFF"
                    style={styles.headerExploreIcon}
                  />
                  <Text style={styles.headerTitle}>Explore CityLens</Text>
                </View>
                <Text style={styles.headerLocation}>Hoàn Kiếm, Hà Nội</Text>
              </View>

              <View style={styles.headerAvatarWrapper}>
                <Avatar
                  size={40}
                  name={userName}
                  onPress={() => navigation.navigate('Profile')}
                />
              </View>
            </View>

            {/* Middle row: temperature + status + AQI + traffic + 3h forecast */}
            <View style={styles.headerBottomRow}>
              {/* Left side: temperature + AQI + traffic */}
              <View style={styles.headerLeftCol}>
                {loading ? (
                  <ActivityIndicator size="small" color="#FFFFFF" />
                ) : (
                  <>
                    <Text style={styles.temperatureText}>
                      {weatherData?.weather?.temp
                        ? `${Math.round(weatherData.weather.temp)}°C`
                        : '--°C'}
                    </Text>

                    <View style={styles.weatherRow}>
                      <MaterialIcons
                        name={getWeatherIcon(weatherData?.weather?.condition)}
                        size={18}
                        color="#FFFFFF"
                      />
                      <Text style={styles.weatherDescription}>
                        {translateCondition(weatherData?.weather?.condition)}
                      </Text>
                    </View>

                    {/* AQI - Lên trên */}
                      <View style={styles.aqiBadge}>
                        <Text style={styles.aqiText}>
                          AQI: {weatherData?.air_quality?.aqi || '--'}
                        </Text>
                      </View>

                    {/* Giao thông - Xuống dưới */}
                      <View style={styles.trafficBadge}>
                        <Text style={styles.aqiText}>Giao thông: Trung bình</Text>
                    </View>
                  </>
                )}
              </View>

              {/* Right side: 3h forecast */}
              <View style={styles.forecastCol}>
                <Text style={styles.forecastTitle}>Dự báo 3h</Text>
                {loading ? (
                  <ActivityIndicator size="small" color="#FFFFFF" />
                ) : (
                  <View style={styles.forecastRow}>
                    {forecastData.length > 0 ? (
                      forecastData.slice(0, 3).map((item, index) => (
                        <View key={index} style={styles.forecastItem}>
                          <Text style={styles.forecastTime}>
                            {formatTime(item.timestamp)}
                          </Text>
                          <MaterialIcons
                            name={getWeatherIcon(item.condition)}
                            size={20}
                            color="#FFFFFF"
                          />
                          <Text style={styles.forecastTemp}>
                            {item.temp ? `${Math.round(item.temp)}°` : '--°'}
                          </Text>
                        </View>
                      ))
                    ) : (
                      <Text style={styles.forecastTime}>Không có dữ liệu</Text>
                    )}
                  </View>
                )}
              </View>
            </View>
          </LinearGradient>

          {/* Search Bar */}
          <View style={styles.searchContainer}>
            <MaterialIcons name="search" size={20} color="#9CA3AF" style={styles.searchIcon} />
            <TextInput
              style={styles.searchInput}
              placeholder="Tìm kiếm địa điểm, phản ánh, dịch vụ..."
              placeholderTextColor="#9CA3AF"
              value={searchQuery}
              onChangeText={setSearchQuery}
            />
          </View>

          {/* Filter Buttons */}
          <View style={styles.filterContainer}>
            <TouchableOpacity
              style={styles.filterButton}
              onPress={() => handleFilterPress('traffic')}
            >
              <MaterialIcons
                name="traffic"
                size={20}
                color="#20A957"
              />
              <Text style={styles.filterText}>
                Giao thông
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[
                styles.filterButton,
                selectedFilter === 'environment' && styles.filterButtonActive,
              ]}
              onPress={() => handleFilterPress('environment')}
            >
              <MaterialIcons
                name="landscape"
                size={20}
                color={selectedFilter === 'environment' ? '#FFFFFF' : '#20A957'}
              />
              <Text
                style={[
                  styles.filterText,
                  selectedFilter === 'environment' && styles.filterTextActive,
                ]}
              >
                Môi trường
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[
                styles.filterButton,
                selectedFilter === 'report' && styles.filterButtonActive,
              ]}
              onPress={() => handleFilterPress('report')}
            >
              <MaterialIcons
                name="campaign"
                size={20}
                color={selectedFilter === 'report' ? '#FFFFFF' : '#20A957'}
              />
              <Text
                style={[
                  styles.filterText,
                  selectedFilter === 'report' && styles.filterTextActive,
                ]}
              >
                Phản ánh
              </Text>
            </TouchableOpacity>
          </View>

          {/* Gần bạn Section */}
          <View style={styles.nearbySection}>
            <View style={styles.nearbyHeader}>
              <Text style={styles.nearbyTitle}>Gần bạn</Text>
              <TouchableOpacity>
                <Text style={styles.seeAllText}>Xem tất cả</Text>
              </TouchableOpacity>
            </View>

            {NEARBY_CARDS.map((card) => (
              <TouchableOpacity
                key={card.id}
                style={styles.nearbyCard}
                onPress={() => handleCardPress(card)}
              >
                <View style={styles.cardContent}>
                  <Text style={styles.cardTitle}>{card.title}</Text>
                  <Text style={styles.cardDescription}>{card.description}</Text>
                  
                  <View style={styles.cardFooter}>
                    {card.hasAiButton && (
                      <TouchableOpacity
                        style={styles.aiCardButton}
                        onPress={(e) => {
                          e.stopPropagation();
                          handleCardAiPress(card);
                        }}
                      >
                        <MaterialIcons name="smart-toy" size={16} color="#FFFFFF" />
                        <Text style={styles.aiCardButtonText}>AI CityLens</Text>
                        <MaterialIcons name="close" size={14} color="#FFFFFF" style={styles.aiCloseIcon} />
                      </TouchableOpacity>
                    )}
                    {card.distance && (
                      <View style={styles.distanceContainer}>
                        <MaterialIcons name="location-on" size={16} color="#20A957" />
                        <Text style={styles.distanceText}>{card.distance}</Text>
                      </View>
                    )}
                    <View style={styles.categoryBadge}>
                      <Text style={styles.categoryText}>#{card.category}</Text>
                    </View>
                  </View>
                </View>
              </TouchableOpacity>
            ))}
          </View>

          {/* Gợi ý chủ đề Section */}
          <View style={styles.suggestionsSection}>
            <View style={styles.suggestionsHeader}>
              <Text style={styles.suggestionsTitle}>Gợi ý chủ đề</Text>
            </View>
            <View style={styles.suggestionsGrid}>
              <TouchableOpacity
                style={styles.suggestionChip}
                onPress={() => {
                  // Navigate to places
                  console.log('Navigate to places');
                }}
              >
                <MaterialIcons name="place" size={20} color="#20A957" />
                <Text style={styles.suggestionText}>Địa điểm</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.suggestionChip}
                onPress={() => {
                  // Navigate to services
                  console.log('Navigate to services');
                }}
              >
                <MaterialIcons name="room-service" size={20} color="#20A957" />
                <Text style={styles.suggestionText}>Dịch vụ</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.suggestionChip}
                onPress={() => {
                  // Navigate to restaurants
                  console.log('Navigate to restaurants');
                }}
              >
                <MaterialIcons name="restaurant" size={20} color="#20A957" />
                <Text style={styles.suggestionText}>Nhà hàng</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.suggestionChip}
                onPress={() => {
                  // Navigate to hotels
                  console.log('Navigate to hotels');
                }}
              >
                <MaterialIcons name="hotel" size={20} color="#20A957" />
                <Text style={styles.suggestionText}>Khách sạn</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.suggestionChip}
                onPress={() => {
                  // Navigate to hospitals
                  console.log('Navigate to hospitals');
                }}
              >
                <MaterialIcons name="local-hospital" size={20} color="#20A957" />
                <Text style={styles.suggestionText}>Bệnh viện</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.suggestionChip}
                onPress={() => {
                  // Navigate to schools
                  console.log('Navigate to schools');
                }}
              >
                <MaterialIcons name="school" size={20} color="#20A957" />
                <Text style={styles.suggestionText}>Trường học</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.suggestionChip}
                onPress={() => {
                  // Navigate to shopping
                  console.log('Navigate to shopping');
                }}
              >
                <MaterialIcons name="shopping-cart" size={20} color="#20A957" />
                <Text style={styles.suggestionText}>Mua sắm</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.suggestionChip}
                onPress={() => {
                  // Navigate to entertainment
                  console.log('Navigate to entertainment');
                }}
              >
                <MaterialIcons name="movie" size={20} color="#20A957" />
                <Text style={styles.suggestionText}>Giải trí</Text>
              </TouchableOpacity>
            </View>
          </View>
        </ScrollView>

        {/* NÚT AI NỔI */}
        {showAiButton && (
          <TouchableOpacity
            activeOpacity={0.8}
            onPress={handleAiPress}
            style={[
              styles.aiButton,
              {
                bottom: aiBottom,
                right: aiRight,
              },
            ]}
          >
            <MaterialIcons name="smart-toy" size={26} color="#FFFFFF" />
          </TouchableOpacity>
        )}
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#EFEFEF',
  },
  root: {
    flex: 1,
  },
  scroll: {
    flex: 1,
  },
  scrollContent: {
    paddingBottom: 32,
  },
  header: {
    height: 280,
    paddingHorizontal: 16,
    paddingTop: Platform.OS === 'android' ? 24 : 8,
    paddingBottom: 16,
    borderBottomLeftRadius: 24,
    borderBottomRightRadius: 24,
  },
  headerTopRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 24,
  },
  headerTitleRow: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  headerExploreIcon: {
    marginRight: 8,
  },
  headerTitle: {
    color: '#FFFFFF',
    fontSize: 22,
    fontWeight: '600',
  },
  headerLocation: {
    marginTop: 4,
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '400',
  },
  headerAvatarWrapper: {
    width: 40,
    height: 40,
  },
  headerBottomRow: {
    flex: 1,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
  },
  headerLeftCol: {
    flex: 1,
  },
  temperatureText: {
    color: '#FFFFFF',
    fontSize: 45,
    fontWeight: '700',
  },
  weatherRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: 4,
  },
  weatherDescription: {
    marginLeft: 8,
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '400',
  },
  aqiBadge: {
    width: 65, // Bằng nửa giao thông (130 / 2)
    height: 30,
    borderRadius: 12,
    backgroundColor: '#67E87A',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 8,
  },
  trafficBadge: {
    minWidth: 100,
    height: 30,
    borderRadius: 12,
    backgroundColor: '#67E87A',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 8,
  },
  aqiText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
  },
  forecastCol: {
    marginLeft: 8,
    alignItems: 'flex-start',
  },
  forecastTitle: {
    marginBottom: 8,
    marginRight: 20,
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '300',
  },
  forecastRow: {
    flexDirection: 'row',
    marginRight: 10,
  },
  forecastItem: {
    alignItems: 'center',
    marginRight: 12,
  },
  forecastTime: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '300',
    marginBottom: 4,
  },
  forecastTemp: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '300',
    marginTop: 4,
  },
  searchContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    marginHorizontal: 16,
    marginTop: 16,
    marginBottom: 12,
    borderRadius: 12,
    paddingHorizontal: 12,
    height: 48,
    elevation: 2,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 4,
  },
  searchIcon: {
    marginRight: 8,
  },
  searchInput: {
    flex: 1,
    fontSize: 14,
    color: '#111827',
  },
  filterContainer: {
    flexDirection: 'row',
    paddingHorizontal: 16,
    marginBottom: 16,
    gap: 8,
  },
  filterButton: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#20A957',
    gap: 6,
  },
  filterButtonActive: {
    backgroundColor: '#20A957',
    borderColor: '#20A957',
  },
  filterText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#20A957',
  },
  filterTextActive: {
    color: '#FFFFFF',
  },
  nearbySection: {
    paddingHorizontal: 16,
    paddingTop: 8,
  },
  nearbyHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  nearbyTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
  },
  suggestionsSection: {
    paddingHorizontal: 16,
    paddingTop: 24,
    marginTop: 8,
  },
  suggestionsHeader: {
    marginBottom: 16,
  },
  suggestionsTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
  },
  suggestionsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  suggestionChip: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    width: '48%',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
    marginBottom: 12,
  },
  suggestionText: {
    marginLeft: 8,
    fontSize: 14,
    fontWeight: '500',
    color: '#111827',
  },
  seeAllText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#20A957',
  },
  nearbyCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    elevation: 2,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 4,
  },
  cardContent: {
    flex: 1,
  },
  cardTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 6,
  },
  cardDescription: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 12,
    lineHeight: 20,
  },
  cardFooter: {
    flexDirection: 'row',
    alignItems: 'center',
    flexWrap: 'wrap',
    gap: 8,
  },
  aiCardButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#20A957',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 16,
    gap: 4,
  },
  aiCardButtonText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#FFFFFF',
  },
  aiCloseIcon: {
    marginLeft: 4,
  },
  distanceContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  distanceText: {
    fontSize: 12,
    color: '#20A957',
    fontWeight: '500',
  },
  categoryBadge: {
    backgroundColor: '#F0FDF4',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  categoryText: {
    fontSize: 12,
    fontWeight: '500',
    color: '#20A957',
  },
  aiButton: {
    position: 'absolute',
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#20A957',
    alignItems: 'center',
    justifyContent: 'center',
    elevation: 5,
    shadowColor: '#000',
    shadowOpacity: 0.25,
    shadowOffset: { width: 0, height: 2 },
    shadowRadius: 4,
  },
});

export default ExploreScreen;

