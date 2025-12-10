// Copyright (c) 2025 CityLens Contributors

// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import React, { useState, useEffect, useRef } from 'react';
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
  Image,
  Animated,
  PanResponder,
  Modal,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialIcons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import Avatar from '../components/Avatar';
import { authService, User } from '../services/auth';
import { weatherService, RealtimeWeatherResponse, ForecastPoint } from '../services/weather';
import reportsService, { Report } from '../services/reports';
import { alertsService, AlertItem } from '../services/alerts';

// Ngã Tư Sở - Quận Thanh Xuân, Hà Nội
const DEFAULT_LOCATION = {
  lat: 21.003204,
  lon: 105.819673,
};
const DEFAULT_LOCATION_NAME = 'Ngã Tư Sở, Quận Thanh Xuân, Hà Nội';

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
  report?: Report;
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

// Helper function to calculate distance between two coordinates (Haversine formula)
const calculateDistance = (lat1: number, lon1: number, lat2: number, lon2: number): number => {
  const R = 6371; // km
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a =
    Math.sin(dLat / 2) * Math.sin(dLat / 2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon / 2) * Math.sin(dLon / 2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
  return R * c;
};

const formatDistance = (distanceKm: number): string => {
  if (distanceKm < 1) return `${Math.round(distanceKm * 1000)}m`;
  return `${distanceKm.toFixed(1)}km`;
};

const mapReportTypeToCategory = (reportType: string): 'Giao thông' | 'Môi trường' | 'Phản ánh' => {
  const type = reportType.toLowerCase();
  if (type.includes('tắc') || type.includes('giao thông') || type.includes('đèn')) return 'Giao thông';
  if (type.includes('rác') || type.includes('ô nhiễm') || type.includes('môi trường')) return 'Môi trường';
  return 'Phản ánh';
};

const formatDateTime = (iso?: string): string => {
  if (!iso) return '';
  const d = new Date(iso);
  if (isNaN(d.getTime())) return '';
  const hh = d.getHours().toString().padStart(2, '0');
  const mm = d.getMinutes().toString().padStart(2, '0');
  const dd = d.getDate().toString().padStart(2, '0');
  const mo = (d.getMonth() + 1).toString().padStart(2, '0');
  const yyyy = d.getFullYear();
  return `${hh}:${mm} ${dd}/${mo}/${yyyy}`;
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
  const [userName, setUserName] = useState<string | undefined>(undefined);
  
  // AI Button drag and drop
  const aiButtonPan = useRef(new Animated.ValueXY({ x: 0, y: 0 })).current;
  const [isDragging, setIsDragging] = useState(false);
  const aiButtonPanResponder = useRef(
    PanResponder.create({
      onStartShouldSetPanResponder: () => true,
      onMoveShouldSetPanResponder: (_, gestureState) => {
        // Chỉ kéo thả khi di chuyển đủ xa (tránh conflict với click)
        return Math.abs(gestureState.dx) > 5 || Math.abs(gestureState.dy) > 5;
      },
      onPanResponderGrant: () => {
        setIsDragging(true);
        aiButtonPan.setOffset({
          x: (aiButtonPan.x as any)._value,
          y: (aiButtonPan.y as any)._value,
        });
      },
      onPanResponderMove: Animated.event(
        [null, { dx: aiButtonPan.x, dy: aiButtonPan.y }],
        { useNativeDriver: false }
      ),
      onPanResponderRelease: () => {
        setIsDragging(false);
        aiButtonPan.flattenOffset();
      },
    })
  ).current;
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFilter, setSelectedFilter] = useState<string | null>('report');
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const [bannerAlert, setBannerAlert] = useState<AlertItem | null>(null);
  const bannerTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const lastAlertIdRef = useRef<string | null>(null);
  
  // Weather data states
  const [weatherData, setWeatherData] = useState<RealtimeWeatherResponse | null>(null);
  const [forecastData, setForecastData] = useState<ForecastPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [userLocation] = useState<{ lat: number; lon: number }>({
    lat: DEFAULT_LOCATION.lat,
    lon: DEFAULT_LOCATION.lon,
  });
  const [locationId, setLocationId] = useState<string | null>(null);
  const [selectedCard, setSelectedCard] = useState<NearbyCard | null>(null);
  const [communityReports, setCommunityReports] = useState<NearbyCard[]>([]);
  const [loadingCommunity, setLoadingCommunity] = useState(true);
  const [hasLoadedCommunity, setHasLoadedCommunity] = useState(false);

  useEffect(() => {
    loadUserInfo();
    loadWeatherData();
    loadCommunityReports();
  }, []);

  // Poll alerts every 90s; if new -> show banner
  useEffect(() => {
    let interval: ReturnType<typeof setInterval> | null = null;

    const fetchAlerts = async () => {
      try {
        const data = await alertsService.list();
        setAlerts(data);
        if (data.length > 0) {
          const latest = data[0];
          if (latest?._id && latest._id !== lastAlertIdRef.current) {
            lastAlertIdRef.current = latest._id;
            setBannerAlert(latest);
            if (bannerTimeoutRef.current) clearTimeout(bannerTimeoutRef.current);
            bannerTimeoutRef.current = setTimeout(() => setBannerAlert(null), 10000);
          }
        }
      } catch (err) {
        console.warn('Fetch alerts failed', err);
      }
    };

    fetchAlerts();
    interval = setInterval(fetchAlerts, 90000); // 1.5 phút

    return () => {
      if (interval) clearInterval(interval);
      if (bannerTimeoutRef.current) clearTimeout(bannerTimeoutRef.current);
    };
  }, []);

  // Khi người dùng bấm filter "Phản ánh" lần đầu thì đảm bảo đã load dữ liệu
  useEffect(() => {
    if (selectedFilter === 'report' && !hasLoadedCommunity) {
      loadCommunityReports();
    }
  }, [selectedFilter, hasLoadedCommunity]);

  useEffect(() => {
    if (locationId) {
      loadForecastData();
    }
  }, [locationId]);

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

  const loadCommunityReports = async () => {
    try {
      setLoadingCommunity(true);
      console.log('[Explore] Fetching community reports...');
      const response = await reportsService.getReports({ limit: 5 });
      if (response.success && response.data) {
          console.log('[Explore] Fetched reports:', response.data.length);
        const cards: NearbyCard[] = response.data
          .filter((report: Report) => report.location)
          .map((report: Report) => {
            const reportLat = report.location?.lat || 0;
            const reportLon = report.location?.lng || 0;
            const distanceKm = calculateDistance(
              userLocation.lat,
              userLocation.lon,
              reportLat,
              reportLon
            );
            return {
              id: report._id,
              title: report.title || report.reportType,
              description: report.content || '',
              distance: formatDistance(distanceKm),
              category: mapReportTypeToCategory(report.reportType),
              hasAiButton: false,
              report,
            };
          })
          .sort((a, b) => {
            const da = parseFloat(a.distance?.replace('km', '') || '0');
            const db = parseFloat(b.distance?.replace('km', '') || '0');
            return da - db;
          })
          .slice(0, 5);
        setCommunityReports(cards);
      } else {
        console.log('[Explore] No reports data');
        setCommunityReports([]);
      }
    } catch (error) {
      console.error('Error loading community reports:', error);
      setCommunityReports([]);
    } finally {
      setLoadingCommunity(false);
      setHasLoadedCommunity(true);
    }
  };

  const handleBackgroundPress = () => {
    Keyboard.dismiss();
  };

  const handleAiPress = () => {
    navigation.navigate('AiAssistant');
  };

  const handleFilterPress = (filter: string) => {
    // Toggle filter for nearby cards
    setSelectedFilter(selectedFilter === filter ? null : filter);
  };

  const reportList = communityReports.length > 0 ? communityReports : NEARBY_CARDS;

  const handleCardPress = (card: NearbyCard) => {
    if (card.report?.media && card.report.media.length > 0) {
      console.log('[Explore] Selected report media URIs:', card.report.media.map((m) => m.uri));
    }
    setSelectedCard(card);
  };

  const handleCloseCard = () => {
    setSelectedCard(null);
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
                  <Text style={styles.headerTitle}>Explore CityLens</Text>
                </View>
                <Text style={styles.headerLocation}>{DEFAULT_LOCATION_NAME}</Text>
              </View>

              <View style={styles.headerAvatarWrapper}>
                <Avatar
                  size={48}
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
                <Text style={styles.forecastTitle}>Dự báo</Text>
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

        {/* Environment detail quick action (text link) */}
        <TouchableOpacity
          style={styles.envLink}
          onPress={() =>
            navigation.navigate('EnvironmentDetail', {
              locationId: locationId,
              userLocation: userLocation,
            })
          }
        >
          <Text style={styles.envLinkText}>Xem chi tiết thông tin môi trường</Text>
        </TouchableOpacity>
          </LinearGradient>

          {bannerAlert ? (
            <TouchableOpacity
              style={styles.alertBanner}
              onPress={() => navigation.navigate('Notifications')}
              activeOpacity={0.85}
            >
              <View style={styles.alertBannerRow}>
                <MaterialIcons name="notifications-active" size={20} color="#0F5132" />
                <Text style={styles.alertBannerTitle}>{bannerAlert.title}</Text>
              </View>
              {bannerAlert.description ? (
                <Text style={styles.alertBannerDesc} numberOfLines={2}>
                  {bannerAlert.description}
                </Text>
              ) : null}
            </TouchableOpacity>
          ) : null}

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
          </View>

          {/* Gần bạn Section */}
          <View style={styles.nearbySection}>
            <View style={styles.nearbyHeader}>
              <Text style={styles.nearbyTitle}>Gần bạn</Text>
              <TouchableOpacity onPress={() => navigation.navigate('Report')}>
                <Text style={styles.seeAllText}>Xem tất cả</Text>
              </TouchableOpacity>
            </View>

            {(selectedFilter === 'report' ? reportList : NEARBY_CARDS)
              .filter((card) => {
                if (!selectedFilter || selectedFilter === 'report') return true;
                return card.category === (selectedFilter === 'traffic'
                  ? 'Giao thông'
                  : selectedFilter === 'environment'
                  ? 'Môi trường'
                  : 'Phản ánh');
              })
              .map((card) => (
              <TouchableOpacity
                key={card.id}
                style={styles.nearbyCard}
                onPress={() => handleCardPress(card)}
              >
                <View style={styles.cardContent}>
                  <Text style={styles.cardTitle}>{card.title}</Text>
                  <Text style={styles.cardDescription}>{card.description}</Text>
                {card.report?.media && card.report.media.length > 0 && (
                  <View style={styles.cardMediaPreview}>
                    {card.report.media[0].type === 'video' ? (
                      <View style={styles.videoContainerSmall}>
                        <MaterialIcons name="videocam" size={28} color="#FFFFFF" />
                        <View style={styles.videoBadgeSmall}>
                          <MaterialIcons name="play-circle-filled" size={20} color="#FFFFFF" />
                        </View>
                      </View>
                    ) : (
                      <Image
                        source={{ uri: card.report.media[0].uri }}
                        style={styles.mediaImageSmall}
                        resizeMode="cover"
                      />
                    )}
                  </View>
                )}
                  
                  <View style={styles.cardFooter}>
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
              {[
                { key: 'atm', label: 'ATM', icon: 'local-atm' },
                { key: 'bank', label: 'Ngân hàng', icon: 'account-balance' },
                { key: 'restaurant', label: 'Nhà hàng/Quán ăn', icon: 'restaurant' },
                { key: 'cafe', label: 'Quán cafe', icon: 'local-cafe' },
                { key: 'pharmacy', label: 'Hiệu thuốc', icon: 'medical-services' },
                { key: 'hospital', label: 'Bệnh viện/Phòng khám', icon: 'local-hospital' },
                { key: 'supermarket', label: 'Siêu thị', icon: 'shopping-cart' },
                { key: 'mall', label: 'Trung tâm TM', icon: 'store-mall-directory' },
                { key: 'shop', label: 'Cửa hàng', icon: 'storefront' },
                { key: 'hotel', label: 'Khách sạn', icon: 'hotel' },
                { key: 'attraction', label: 'Điểm tham quan', icon: 'flag' },
                { key: 'park', label: 'Công viên', icon: 'park' },
              ].map((item) => (
                <TouchableOpacity
                  key={item.key}
                  style={styles.suggestionChip}
                  onPress={() => navigation.navigate('Map', { poiCategory: item.key })}
                >
                  <MaterialIcons name={item.icon as any} size={20} color="#20A957" />
                  <Text style={styles.suggestionText}>{item.label}</Text>
                </TouchableOpacity>
              ))}
            </View>
          </View>
        </ScrollView>

        {/* NÚT AI NỔI */}
        {showAiButton && (
          <Animated.View
            style={[
              styles.aiButton,
              {
                bottom: 24,
                right: 24,
                transform: aiButtonPan.getTranslateTransform(),
              },
            ]}
            {...aiButtonPanResponder.panHandlers}
          >
            <TouchableOpacity
              activeOpacity={0.8}
              onPress={() => {
                if (!isDragging) {
                  handleAiPress();
                }
              }}
              style={styles.aiButtonContent}
            >
              <MaterialIcons name="auto-awesome" size={26} color="#FFFFFF" />
            </TouchableOpacity>
          </Animated.View>
        )}
      </View>

      {/* Modal chi tiết phản ánh */}
      <Modal
        visible={!!selectedCard}
        transparent
        animationType="slide"
        onRequestClose={handleCloseCard}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Chi tiết phản ánh</Text>
              <TouchableOpacity onPress={handleCloseCard}>
                <MaterialIcons name="close" size={24} color="#111827" />
              </TouchableOpacity>
            </View>
            {selectedCard && (
              <View style={styles.modalBody}>
                <Text style={styles.cardTitle}>{selectedCard.title}</Text>
                <Text style={styles.cardDescription}>{selectedCard.description}</Text>
                <View style={styles.modalMeta}>
                  <View style={[styles.categoryBadge, { marginRight: 8 }]}>
                    <Text style={styles.categoryText}>#{selectedCard.category}</Text>
                  </View>
                  {selectedCard.distance && (
                    <View style={styles.distanceContainer}>
                      <MaterialIcons name="location-on" size={16} color="#20A957" />
                      <Text style={styles.distanceText}>{selectedCard.distance}</Text>
                    </View>
                  )}
                </View>
                {selectedCard.report?.media && selectedCard.report.media.length > 0 ? (
                  <View style={styles.mediaItem}>
                    {selectedCard.report.media[0].type === 'video' ? (
                      <View style={styles.videoContainer}>
                        <MaterialIcons name="videocam" size={36} color="#FFFFFF" />
                        <View style={styles.videoBadge}>
                          <MaterialIcons name="play-circle-filled" size={28} color="#FFFFFF" />
                        </View>
                      </View>
                    ) : (
                      <Image
                        source={{ uri: selectedCard.report.media[0].uri }}
                        style={styles.mediaImage}
                        resizeMode="cover"
                      />
                    )}
                  </View>
                ) : (
                  <View style={styles.mediaPlaceholder}>
                    <MaterialIcons name="image" size={36} color="#9CA3AF" />
                    <Text style={styles.mediaPlaceholderText}>Không có ảnh/video</Text>
                  </View>
                )}
                {selectedCard.report && (
                  <View style={styles.modalInfoBox}>
                    <View style={styles.modalInfoRow}>
                      <MaterialIcons name="category" size={18} color="#6B7280" />
                      <Text style={styles.modalInfoText}>
                        {selectedCard.report.reportType || 'Không có loại'}
                      </Text>
                    </View>
                    <View style={styles.modalInfoRow}>
                      <MaterialIcons name="place" size={18} color="#6B7280" />
                      <Text style={styles.modalInfoText}>
                        {selectedCard.report.addressDetail ||
                          selectedCard.report.ward ||
                          'Không có địa chỉ'}
                      </Text>
                    </View>
                    <View style={styles.modalInfoRow}>
                      <MaterialIcons name="schedule" size={18} color="#6B7280" />
                      <Text style={styles.modalInfoText}>
                        {formatDateTime(selectedCard.report.createdAt) || '---'}
                      </Text>
                    </View>
                    <View style={styles.modalInfoRow}>
                      <MaterialIcons name="info" size={18} color="#6B7280" />
                      <Text style={styles.modalInfoText}>
                        {selectedCard.report.status || 'pending'}
                      </Text>
                    </View>
                  </View>
                )}
                <TouchableOpacity
                  style={styles.modalButton}
                  onPress={() => {
                    handleCloseCard();
                    navigation.navigate('Map', {
                      layerType:
                        selectedCard.category === 'Giao thông'
                          ? 'traffic'
                          : selectedCard.category === 'Môi trường'
                          ? 'environment'
                          : 'reports',
                    });
                  }}
                >
                  <Text style={styles.modalButtonText}>Mở trên bản đồ</Text>
                </TouchableOpacity>
              </View>
            )}
          </View>
        </View>
      </Modal>
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
    width: 24,
    height: 24,
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
    width: 48,
    height: 48,
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
    backgroundColor: '#FFFFFF',
    borderWidth: 2,
    borderColor: '#20A957',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 8,
  },
  trafficBadge: {
    alignSelf: 'flex-start',
    height: 30,
    borderRadius: 12,
    backgroundColor: '#FFFFFF',
    borderWidth: 2,
    borderColor: '#20A957',
    alignItems: 'flex-start',
    justifyContent: 'center',
    paddingHorizontal: 12,
    marginTop: 8,
  },
  aqiText: {
    color: '#20A957',
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
  alertBanner: {
    marginHorizontal: 16,
    marginTop: 12,
    backgroundColor: '#D1E7DD',
    borderColor: '#0F5132',
    borderWidth: 1,
    borderRadius: 12,
    padding: 12,
    gap: 6,
  },
  alertBannerRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  alertBannerTitle: {
    flex: 1,
    fontSize: 15,
    fontWeight: '700',
    color: '#0F5132',
  },
  alertBannerDesc: {
    color: '#0F5132',
    fontSize: 13,
    lineHeight: 18,
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
  envLink: {
    marginTop: 8,
    marginLeft: 16,
  },
  envLinkText: {
    fontSize: 13,
    fontWeight: '600',
    color: '#FFFFFF',
    textDecorationLine: 'underline',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0,0,0,0.4)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  modalContent: {
    width: '100%',
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    shadowColor: '#000',
    shadowOpacity: 0.1,
    shadowOffset: { width: 0, height: 4 },
    shadowRadius: 6,
    elevation: 4,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#111827',
  },
  modalBody: {
    gap: 12,
  },
  modalMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  modalButton: {
    marginTop: 8,
    backgroundColor: '#20A957',
    borderRadius: 12,
    paddingVertical: 12,
    alignItems: 'center',
    justifyContent: 'center',
  },
  modalButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
  },
  modalInfoBox: {
    marginTop: 8,
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    padding: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    gap: 8,
  },
  modalInfoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
  },
  modalInfoText: {
    fontSize: 14,
    color: '#374151',
    flexShrink: 1,
  },
  mediaScrollView: {
    maxHeight: 220,
    marginVertical: 8,
  },
  mediaItem: {
    width: '100%',
    height: 200,
  },
  mediaImage: {
    width: '100%',
    height: '100%',
    borderRadius: 12,
  },
  cardMediaPreview: {
    height: 140,
    borderRadius: 12,
    overflow: 'hidden',
    backgroundColor: '#F3F4F6',
    marginTop: 8,
    marginBottom: 4,
  },
  mediaImageSmall: {
    width: '100%',
    height: '100%',
  },
  videoContainerSmall: {
    width: '100%',
    height: '100%',
    backgroundColor: '#1F2937',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
  },
  videoBadgeSmall: {
    position: 'absolute',
    bottom: 8,
    right: 8,
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    borderRadius: 12,
    padding: 4,
  },
  videoContainer: {
    width: '100%',
    height: '100%',
    backgroundColor: '#1F2937',
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: 12,
    position: 'relative',
  },
  videoBadge: {
    position: 'absolute',
    bottom: 12,
    right: 12,
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    borderRadius: 16,
    padding: 6,
  },
  mediaPlaceholder: {
    width: '100%',
    height: 140,
    backgroundColor: '#F3F4F6',
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 6,
    marginVertical: 8,
  },
  mediaPlaceholderText: {
    fontSize: 13,
    color: '#9CA3AF',
  },
  aiButton: {
    position: 'absolute',
    width: 60,
    height: 60,
    borderRadius: 30,
    backgroundColor: '#20A957',
    alignItems: 'center',
    justifyContent: 'center',
  },
  aiButtonContent: {
    width: '100%',
    height: '100%',
    borderRadius: 30,
    alignItems: 'center',
    justifyContent: 'center',
  },
});

export default ExploreScreen;

