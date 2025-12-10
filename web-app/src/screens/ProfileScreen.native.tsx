// Copyright (c) 2025 CityLens Contributors

// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ScrollView, Alert } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialIcons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';
import Avatar from '../components/Avatar';
import { useAuth } from '../contexts/AuthContext';
import Constants from 'expo-constants';

const ProfileScreen: React.FC = () => {
  const navigation = useNavigation<any>();
  const { user, logout } = useAuth();
  const userName = user?.full_name || user?.username || 'Người dùng';
  const userEmail = user?.email || 'user@example.com';
  const appVersion =
    (Constants.expoConfig as any)?.version ||
    (Constants.expoConfig as any)?.extra?.appVersion ||
    '1.0.0';

  const handleLogout = async () => {
    try {
      await logout();
      // Navigation will be handled by RootNavigator based on auth state
    } catch (error) {
      console.error('Logout error:', error);
      Alert.alert('Lỗi', 'Không thể đăng xuất. Vui lòng thử lại.');
    }
  };

  const renderItem = (
    label: string,
    icon: keyof typeof MaterialIcons.glyphMap,
    onPress: () => void
  ) => (
    <TouchableOpacity style={styles.menuItem} onPress={onPress}>
      <MaterialIcons name={icon} size={22} color="#111827" style={styles.menuIcon} />
      <Text style={styles.menuText}>{label}</Text>
      <MaterialIcons name="chevron-right" size={22} color="#9CA3AF" />
    </TouchableOpacity>
  );

  const handleSupport = () => {
    navigation.navigate('Support' as never, {
      info: 'Nếu gặp sự cố, vui lòng liên hệ:\n• Email: support@citylens.app\n• Điện thoại: 1900-1234\n• Thời gian: 8:00 - 21:00 hàng ngày',
    } as never);
  };

  const handleTerms = () => {
    navigation.navigate('Terms' as never, {
      content:
        'Bằng việc sử dụng ứng dụng, bạn đồng ý với các điều khoản về bảo mật dữ liệu, giới hạn trách nhiệm, và tuân thủ pháp luật hiện hành.',
    } as never);
  };

  const handleInvite = () => {
    Alert.alert('Mời bạn bè', 'Tính năng sẽ sớm ra mắt.');
  };

  const handleCountry = () => {
    Alert.alert('Quốc gia', 'Tính năng đang được phát triển.');
  };

  const handleNotifications = () => {
    Alert.alert('Cài đặt thông báo', 'Tính năng đang được phát triển.');
  };

  const handleEditProfile = () => {
    navigation.navigate('PersonalInfo' as never);
  };

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>Hồ sơ</Text>
      </View>

      <ScrollView style={styles.content} contentContainerStyle={styles.contentContainer}>
        <View style={styles.avatarSection}>
          <Avatar size={80} name={userName} />
          <Text style={styles.name}>{userName}</Text>
          <Text style={styles.email}>{userEmail}</Text>
        </View>

        {/* Account Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Tài khoản</Text>
          <View style={styles.menuSection}>
            {renderItem('Quốc gia', 'public', handleCountry)}
            {renderItem('Cài đặt thông báo', 'notifications-none', handleNotifications)}
            {renderItem('Chỉnh sửa hồ sơ', 'person-outline', handleEditProfile)}
          </View>
        </View>

        {/* General Section */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Chung</Text>
          <View style={styles.menuSection}>
            {renderItem('Hỗ trợ', 'help-outline', handleSupport)}
            {renderItem('Điều khoản sử dụng', 'description', handleTerms)}
            {renderItem(`Phiên bản ứng dụng ${appVersion}`, 'info-outline', () =>
              Alert.alert('Phiên bản ứng dụng', appVersion)
            )}
          </View>
        </View>

        <TouchableOpacity
          style={[styles.menuItem, styles.logoutItem]}
          onPress={handleLogout}
        >
          <MaterialIcons name="logout" size={22} color="#E74C3C" style={styles.menuIcon} />
          <Text style={[styles.menuText, styles.logoutText]}>Đăng xuất</Text>
          <MaterialIcons name="chevron-right" size={22} color="#E5E7EB" />
        </TouchableOpacity>
      </ScrollView>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  header: {
    backgroundColor: '#FFFFFF',
    paddingTop: 16,
    paddingBottom: 24,
    paddingHorizontal: 16,
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerTitle: {
    fontSize: 24,
    fontWeight: '700',
    color: '#20A957',
    textAlign: 'center',
  },
  content: {
    flex: 1,
  },
  contentContainer: {
    padding: 24,
  },
  avatarSection: {
    alignItems: 'center',
    marginBottom: 32,
  },
  name: {
    fontSize: 20,
    fontWeight: '600',
    color: '#111827',
    marginTop: 16,
  },
  email: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 4,
  },
  section: {
    marginBottom: 24,
  },
  sectionTitle: {
    fontSize: 13,
    fontWeight: '600',
    color: '#6B7280',
    marginBottom: 8,
    textTransform: 'uppercase',
  },
  menuSection: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    overflow: 'hidden',
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  menuIcon: {
    width: 24,
    textAlign: 'center',
  },
  menuText: {
    flex: 1,
    fontSize: 16,
    color: '#111827',
    marginLeft: 12,
  },
  logoutItem: {
    borderTopWidth: 1,
    borderTopColor: '#F3F4F6',
    marginTop: 8,
  },
  logoutText: {
    color: '#E74C3C',
  },
});

export default ProfileScreen;

