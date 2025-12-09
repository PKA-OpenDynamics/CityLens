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
import { MaterialIcons } from '@expo/vector-icons';
import { useNavigation } from '@react-navigation/native';

interface ReportItem {
  id: string;
  title: string;
  address: string;
  time: string;
  status: string;
  imageUrl: string;
  category: string;
}

const ReportScreen: React.FC = () => {
  const navigation = useNavigation<any>();
  const [bottomIndex, setBottomIndex] = useState(0); // 0: Cộng đồng, 1: Cá nhân
  const [selectedCategory, setSelectedCategory] = useState('Tất cả');

  // Mock data
  const communityReports: ReportItem[] = [
    {
      id: '1',
      title: 'Tình trạng xả rác bừa bãi xảy ra thường xuyên tại khu đô thị mới',
      address: '77 Trần Nhân Tông, Phường X',
      time: '1 ngày trước',
      status: 'Đã xử lý',
      imageUrl: 'https://images.unsplash.com/photo-1528323273322-d81458248d40?auto=format&fit=crop&w=400&q=80',
      category: 'Văn minh đô thị',
    },
    {
      id: '2',
      title: 'Xả rác thải dân dụng bừa bãi ở ngã tư vị trí thu gom rác thải',
      address: '227 Phạm Văn Đồng, Phường Y',
      time: '2 ngày trước',
      status: 'Đã xử lý',
      imageUrl: 'https://picsum.photos/seed/report2/400/200',
      category: 'Văn minh đô thị',
    },
    {
      id: '3',
      title: 'Chưa xử lý việc lấn chiếm trồng cây, lấn chiếm vỉa hè',
      address: '17 Trần Hữu Dực, Phường Z',
      time: '4 ngày trước',
      status: 'Đã xử lý',
      imageUrl: 'https://images.unsplash.com/photo-1501183638710-841dd1904471?auto=format&fit=crop&w=400&q=80',
      category: 'Văn minh đô thị',
    },
    {
      id: '4',
      title: 'Có người lạ đang hành vi đáng nghi tại khu vực công cộng',
      address: '123 Nguyễn Trãi, Phường A',
      time: '3 giờ trước',
      status: 'Chờ xử lý',
      imageUrl: 'https://images.unsplash.com/photo-1557804506-669a67965ba0?auto=format&fit=crop&w=400&q=80',
      category: 'An ninh trật tự',
    },
    {
      id: '5',
      title: 'Phát hiện hành vi trộm cắp tại cửa hàng tiện lợi',
      address: '456 Lê Lợi, Phường B',
      time: '5 giờ trước',
      status: 'Đã tiếp nhận',
      imageUrl: 'https://picsum.photos/seed/report5/400/200',
      category: 'An ninh trật tự',
    },
    {
      id: '6',
      title: 'Xe đạp để sai quy định gây cản trở giao thông',
      address: '789 Hoàng Diệu, Phường C',
      time: '6 giờ trước',
      status: 'Đã xử lý',
      imageUrl: 'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?auto=format&fit=crop&w=400&q=80',
      category: 'Văn minh đô thị',
    },
    {
      id: '7',
      title: 'Quảng cáo, rao vặt dán trái phép trên cột điện',
      address: '321 Trường Chinh, Phường D',
      time: '1 ngày trước',
      status: 'Chờ xử lý',
      imageUrl: 'https://picsum.photos/seed/report7/400/200',
      category: 'Văn minh đô thị',
    },
    {
      id: '8',
      title: 'Nhóm người tụ tập gây ồn ào vào ban đêm',
      address: '654 Điện Biên Phủ, Phường E',
      time: '2 ngày trước',
      status: 'Đã tiếp nhận',
      imageUrl: 'https://images.unsplash.com/photo-1511632765486-a01980e01a18?auto=format&fit=crop&w=400&q=80',
      category: 'An ninh trật tự',
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
            onPress={() => setSelectedCategory(category)}
            style={[
              styles.categoryChip,
              selectedCategory === category && styles.categoryChipActive,
            ]}
          >
            <Text
              style={[
                styles.categoryChipText,
                selectedCategory === category && styles.categoryChipTextActive,
              ]}
            >
              {category}
            </Text>
          </TouchableOpacity>
        ))}
      </ScrollView>
    );
  };

  const filteredReports = bottomIndex === 0
    ? selectedCategory === 'Tất cả'
      ? communityReports
      : communityReports.filter(report => report.category === selectedCategory)
    : [];

  return (
    <SafeAreaView style={styles.container}>
      <View style={styles.header}>
        <TouchableOpacity
          onPress={() => navigation.goBack()}
          style={styles.backButton}
        >
          <MaterialIcons name="arrow-back" size={24} color="#20A957" />
        </TouchableOpacity>
        <Text style={styles.headerTitle}>Phản ánh hiện trường</Text>
      </View>

      <View style={styles.content}>
        {renderCategoryChips()}
        <View style={styles.divider} />

        <View style={styles.tabContent}>
          {bottomIndex === 0 ? (
            <FlatList
              data={filteredReports}
              renderItem={renderReportItem}
              keyExtractor={(item) => item.id}
              contentContainerStyle={styles.listContent}
              showsVerticalScrollIndicator={true}
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
    backgroundColor: '#FFFFFF',
    paddingTop: 16,
    paddingBottom: 24,
    paddingHorizontal: 16,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
  },
  backButton: {
    position: 'absolute',
    left: 16,
    padding: 8,
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
    backgroundColor: '#FFFFFF',
    borderWidth: 2,
    borderColor: '#20A957',
    marginHorizontal: 4,
  },
  categoryChipActive: {
    backgroundColor: '#20A957',
    borderWidth: 2,
    borderColor: '#20A957',
  },
  categoryChipText: {
    fontSize: 14,
    color: '#20A957',
  },
  categoryChipTextActive: {
    color: '#FFFFFF',
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
    marginBottom: 16,
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
