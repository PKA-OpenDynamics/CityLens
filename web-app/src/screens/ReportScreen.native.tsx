// Copyright (c) 2025 CityLens Contributors

// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import React, { useState } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  FlatList,
  Image,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { LinearGradient } from 'expo-linear-gradient';
import { MaterialIcons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';

interface ReportItem {
  id: string;
  title: string;
  address: string;
  time: string;
  status: string;
  imageUrl: string;
}

const ReportScreen: React.FC = () => {
  const navigation = useNavigation<any>();
  const [bottomIndex, setBottomIndex] = useState(0); // 0: Cộng đồng, 1: Cá nhân

  // Mock data
  const communityReports: ReportItem[] = [
    {
      id: '1',
      title: 'Tình trạng xả rác bừa bãi xảy ra thường xuyên tại khu đô thị mới',
      address: '77 Trần Nhân Tông, Phường X',
      time: '1 ngày trước',
      status: 'Đã xử lý',
      imageUrl: 'https://images.unsplash.com/photo-1528323273322-d81458248d40?auto=format&fit=crop&w=400&q=80',
    },
    {
      id: '2',
      title: 'Xả rác thải dân dụng bừa bãi ở ngã tư vị trí thu gom rác thải',
      address: '227 Phạm Văn Đồng, Phường Y',
      time: '2 ngày trước',
      status: 'Đã xử lý',
      imageUrl: 'https://picsum.photos/seed/report2/400/200',
    },
    {
      id: '3',
      title: 'Chưa xử lý việc lấn chiếm trồng cây, lấn chiếm vỉa hè',
      address: '17 Trần Hữu Dực, Phường Z',
      time: '4 ngày trước',
      status: 'Đã xử lý',
      imageUrl: 'https://images.unsplash.com/photo-1501183638710-841dd1904471?auto=format&fit=crop&w=400&q=80',
    },
  ];

  const communityCategories = ['Tất cả', 'An ninh trật tự', 'Văn minh đô thị', 'Giao thông'];
  const personalCategories = ['Tất cả', 'Bản nháp', 'Chờ xử lý', 'Đã tiếp nhận'];

  const renderReportItem = ({ item }: { item: ReportItem }) => (
    <TouchableOpacity
      style={styles.reportCard}
      onPress={() => navigation.navigate('ReportDetail', { report: item })}
    >
      <Image source={{ uri: item.imageUrl }} style={styles.reportImage} />
      <View style={styles.reportContent}>
        <Text style={styles.reportTitle} numberOfLines={2}>
          {item.title}
        </Text>
        <Text style={styles.reportAddress} numberOfLines={1}>
          {item.address}
        </Text>
        <View style={styles.reportFooter}>
          <Text style={styles.reportTime}>{item.time}</Text>
          <Text style={styles.reportStatus}>{item.status}</Text>
        </View>
      </View>
    </TouchableOpacity>
  );

  const renderCategoryChips = () => {
    const categories = bottomIndex === 0 ? communityCategories : personalCategories;
    return (
      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.categoryScroll}
        contentContainerStyle={styles.categoryContainer}
      >
        {categories.map((category, index) => (
          <TouchableOpacity
            key={index}
            style={[
              styles.categoryChip,
              index === 0 && styles.categoryChipActive,
            ]}
          >
            <Text
              style={[
                styles.categoryChipText,
                index === 0 && styles.categoryChipTextActive,
              ]}
            >
              {category}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>
    );
  };

  return (
    <SafeAreaView style={styles.container}>
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
        <TouchableOpacity
          style={styles.headerTitleContainer}
          onPress={() => {
            // Navigate to first report detail if available
            if (communityReports.length > 0) {
              navigation.navigate('ReportDetail', { report: communityReports[0] });
            }
          }}
      >
        <Text style={styles.headerTitle}>Phản ánh hiện trường</Text>
        </TouchableOpacity>
      </LinearGradient>

      <View style={styles.content}>
        {renderCategoryChips()}
        <View style={styles.divider} />

        <View style={styles.tabContent}>
          {bottomIndex === 0 ? (
            <FlatList
              data={communityReports}
              renderItem={renderReportItem}
              keyExtractor={(item) => item.id}
              contentContainerStyle={styles.listContent}
            />
          ) : (
            <View style={styles.emptyState}>
              <Text style={styles.emptyText}>
                Các phản ánh của bạn sẽ hiển thị tại đây.
              </Text>
            </View>
          )}
        </View>
      </View>

      {/* Bottom Navigation */}
      <View style={styles.bottomNav}>
        <TouchableOpacity
          style={styles.bottomNavItem}
          onPress={() => setBottomIndex(0)}
        >
          <MaterialIcons
            name="public"
            size={24}
            color={bottomIndex === 0 ? '#20A957' : '#9CA3AF'}
          />
          <Text
            style={[
              styles.bottomNavLabel,
              bottomIndex === 0 && styles.bottomNavLabelActive,
            ]}
          >
            Cộng đồng
          </Text>
        </TouchableOpacity>

        {/* Floating Action Button - Tích hợp vào bottom nav */}
        <TouchableOpacity
          style={styles.fab}
          onPress={() => navigation.navigate('CreateReport')}
        >
          <MaterialIcons name="add" size={28} color="#FFFFFF" />
        </TouchableOpacity>

        <TouchableOpacity
          style={styles.bottomNavItem}
          onPress={() => setBottomIndex(1)}
        >
          <MaterialIcons
            name="person"
            size={24}
            color={bottomIndex === 1 ? '#20A957' : '#9CA3AF'}
          />
          <Text
            style={[
              styles.bottomNavLabel,
              bottomIndex === 1 && styles.bottomNavLabelActive,
            ]}
          >
            Cá nhân
          </Text>
        </TouchableOpacity>
      </View>
    </SafeAreaView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  header: {
    paddingTop: 16,
    paddingBottom: 24,
    paddingHorizontal: 16,
    flexDirection: 'row',
    alignItems: 'center',
  },
  backButton: {
    padding: 8,
  },
  headerTitleContainer: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  content: {
    flex: 1,
  },
  categoryScroll: {
    maxHeight: 50,
  },
  categoryContainer: {
    paddingHorizontal: 8,
    paddingVertical: 8,
  },
  categoryChip: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 16,
    backgroundColor: '#E5E7EB',
    marginHorizontal: 4,
  },
  categoryChipActive: {
    backgroundColor: '#DBEAFE',
  },
  categoryChipText: {
    fontSize: 14,
    color: '#374151',
  },
  categoryChipTextActive: {
    color: '#2563EB',
    fontWeight: '600',
  },
  divider: {
    height: 1,
    backgroundColor: '#E5E7EB',
  },
  tabContent: {
    flex: 1,
  },
  listContent: {
    padding: 12,
  },
  reportCard: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    borderRadius: 8,
    marginBottom: 8,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.05,
    shadowRadius: 2,
    elevation: 2,
  },
  reportImage: {
    width: 100,
    height: 80,
    backgroundColor: '#E5E7EB',
  },
  reportContent: {
    flex: 1,
    padding: 8,
    justifyContent: 'space-between',
  },
  reportTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 4,
  },
  reportAddress: {
    fontSize: 12,
    color: '#6B7280',
    marginBottom: 4,
  },
  reportFooter: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  reportTime: {
    fontSize: 11,
    color: '#9CA3AF',
    marginRight: 8,
  },
  reportStatus: {
    fontSize: 11,
    color: '#10B981',
    fontWeight: '600',
  },
  emptyState: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  emptyText: {
    fontSize: 16,
    color: '#6B7280',
    textAlign: 'center',
  },
  fab: {
    width: 56,
    height: 56,
    borderRadius: 28,
    backgroundColor: '#20A957',
    alignItems: 'center',
    justifyContent: 'center',
    elevation: 5,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    marginTop: -28, // Nổi lên trên navigation bar
  },
  bottomNav: {
    flexDirection: 'row',
    height: 60,
    backgroundColor: '#FFFFFF',
    borderTopWidth: 0.5,
    borderTopColor: '#E5E7EB',
    paddingHorizontal: 20,
    justifyContent: 'space-around',
    alignItems: 'center',
    paddingBottom: 8, // Thêm padding để FAB không bị che
  },
  bottomNavItem: {
    alignItems: 'center',
    flex: 1,
  },
  bottomNavLabel: {
    fontSize: 11,
    color: '#9CA3AF',
    marginTop: 2,
  },
  bottomNavLabelActive: {
    color: '#20A957',
    fontWeight: '600',
  },
});

export default ReportScreen;
