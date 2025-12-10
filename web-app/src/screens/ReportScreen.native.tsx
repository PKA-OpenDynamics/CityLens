// Copyright (c) 2025 CityLens Contributors

// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  StyleSheet,
  TouchableOpacity,
  ScrollView,
  FlatList,
  Image,
  Alert,
  ActivityIndicator,
  RefreshControl,
  Modal,
  TextInput,
  Dimensions,
  Platform,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { MaterialIcons } from '@expo/vector-icons';
import { useNavigation, useRoute } from '@react-navigation/native';
import reportsService, { Report } from '../services/reports';
import commentsService, { Comment } from '../services/comments';
import { useAuth } from '../contexts/AuthContext';

interface ReportItem extends Report {
  displayStatus: string;
  displayTime: string;
  imageUrl: string;
}

const ReportScreen: React.FC = () => {
  const navigation = useNavigation<any>();
  const route = useRoute<any>();
  const { user } = useAuth();
  const [bottomIndex, setBottomIndex] = useState(0); // 0: Cộng đồng, 1: Cá nhân
  const [selectedCategory, setSelectedCategory] = useState('Tất cả');
  const [communityReports, setCommunityReports] = useState<ReportItem[]>([]);
  const [personalReports, setPersonalReports] = useState<ReportItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedReport, setSelectedReport] = useState<ReportItem | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [comments, setComments] = useState<Comment[]>([]);
  const [newComment, setNewComment] = useState('');
  const [submittingComment, setSubmittingComment] = useState(false);
  const [playingVideo, setPlayingVideo] = useState<{ uri: string; index: number } | null>(null);

  // Helper function to format time
  const formatTime = (dateString: string): string => {
    try {
      // Parse date string - handle both UTC and ISO format
      let date: Date;
      if (typeof dateString === 'string') {
        // If dateString doesn't have timezone info, assume it's UTC
        if (dateString.endsWith('Z') || dateString.includes('+') || dateString.includes('-', 10)) {
          date = new Date(dateString);
        } else {
          // If no timezone, append Z to indicate UTC
          date = new Date(dateString + (dateString.includes('T') ? 'Z' : ''));
        }
      } else {
        date = new Date(dateString);
      }
      
      const now = new Date();
      const diffMs = now.getTime() - date.getTime();
      
      // Handle negative diff (future dates) - should not happen but just in case
      if (diffMs < 0) {
        return 'Vừa xong';
      }
      
      const diffMins = Math.floor(diffMs / 60000);
      const diffHours = Math.floor(diffMs / 3600000);
      const diffDays = Math.floor(diffMs / 86400000);

      if (diffMins < 1) return 'Vừa xong';
      if (diffMins < 60) return `${diffMins} phút trước`;
      if (diffHours < 24) return `${diffHours} giờ trước`;
      if (diffDays < 7) return `${diffDays} ngày trước`;
      return date.toLocaleDateString('vi-VN');
    } catch (error) {
      console.error('Error formatting time:', error, dateString);
      return dateString;
    }
  };

  // Helper function to map status
  const mapStatus = (status: string): string => {
    const statusMap: { [key: string]: string } = {
      'pending': 'Chờ xử lý',
      'processing': 'Đang xử lý',
      'resolved': 'Đã xử lý',
      'rejected': 'Đã từ chối',
      'draft': 'Bản nháp',
    };
    return statusMap[status] || status;
  };

  // Helper function to get first media URL
  const getFirstMediaUrl = (report: Report): string => {
    if (report.media && report.media.length > 0) {
      return report.media[0].uri;
    }
    return '';
  };

  // Transform report data
  const transformReport = useCallback((report: Report): ReportItem => {
    return {
      ...report,
      displayStatus: mapStatus(report.status),
      displayTime: formatTime(report.createdAt),
      imageUrl: getFirstMediaUrl(report),
    };
  }, []);

  // Fetch reports from API
  const fetchReports = useCallback(async (isRefresh = false) => {
    if (isRefresh) {
      setRefreshing(true);
    } else {
      setLoading(true);
    }
    setError(null);

    try {
      if (bottomIndex === 0) {
        // Community reports - no userId filter, but filter by status if needed
        let statusFilter: string | undefined = undefined;
        if (selectedCategory === 'Chờ xử lý') {
          statusFilter = 'pending';
        } else if (selectedCategory === 'Đang xử lý') {
          statusFilter = 'processing';
        } else if (selectedCategory === 'Đã xử lý') {
          statusFilter = 'resolved';
        }

        const response = await reportsService.getReports({
          limit: 50,
          status: statusFilter,
        });

        if (response.success && response.data) {
          const transformed = response.data.map(transformReport);
          setCommunityReports(transformed);
        } else {
          setCommunityReports([]);
        }
      } else {
        // Personal reports - filter by userId
        if (!user?._id && !user?.id) {
          setPersonalReports([]);
          if (isRefresh) {
            setRefreshing(false);
          } else {
            setLoading(false);
          }
          return;
        }

        const userId = user?._id || user?.id;
        let statusFilter: string | undefined = undefined;
        
        if (selectedCategory === 'Bản nháp') {
          statusFilter = 'draft';
        } else if (selectedCategory === 'Chờ xử lý') {
          statusFilter = 'pending';
        } else if (selectedCategory === 'Đang xử lý') {
          statusFilter = 'processing';
        } else if (selectedCategory === 'Đã xử lý') {
          statusFilter = 'resolved';
        }

        const response = await reportsService.getReports({
          limit: 50,
          userId: userId,
          status: statusFilter,
        });

        if (response.success && response.data) {
          const transformed = response.data.map(transformReport);
          setPersonalReports(transformed);
        } else {
          setPersonalReports([]);
        }
      }
    } catch (err: any) {
      console.error('Error fetching reports:', err);
      setError(err.message || 'Không thể tải danh sách báo cáo');
      if (bottomIndex === 0) {
        setCommunityReports([]);
      } else {
        setPersonalReports([]);
      }
    } finally {
      if (isRefresh) {
        setRefreshing(false);
      } else {
        setLoading(false);
      }
    }
  }, [bottomIndex, selectedCategory, user, transformReport]);

  // Show success message if coming from CreateReportScreen and refresh reports
  useEffect(() => {
    if (route.params?.showSuccessMessage) {
      const message = route.params?.message || 'Tạo phản ánh thành công';
      
      // Refresh reports to show the newly created one
      fetchReports(false);
      
      // Use setTimeout to ensure screen is fully mounted before showing alert
      const timer = setTimeout(() => {
        Alert.alert('Thành công', message, [
          {
            text: 'OK',
            onPress: () => {
              // Clear params after alert is dismissed
              navigation.setParams({ showSuccessMessage: false, message: undefined });
            }
          }
        ]);
      }, 100);
      
      return () => clearTimeout(timer);
    }
  }, [route.params?.showSuccessMessage, route.params?.message, navigation, fetchReports]);

  // Fetch reports when tab or category changes
  useEffect(() => {
    fetchReports();
  }, [fetchReports]);

  // Handle pull-to-refresh
  const handleRefresh = useCallback(() => {
    fetchReports(true);
  }, [fetchReports]);

  // Fetch comments for a report
  const fetchComments = async (reportId: string) => {
    if (!reportId) return;
    
    try {
      const commentsData = await commentsService.getComments(reportId);
      setComments(commentsData);
    } catch (err) {
      console.error('Error fetching comments:', err);
      setComments([]);
    }
  };

  // Submit a new comment
  const handleSubmitComment = async () => {
    if (!newComment.trim() || !selectedReport) return;
    
    setSubmittingComment(true);
    try {
      const userId = user?._id || user?.id;
      const userName = user?.full_name || user?.username;
      
      const newCommentData = await commentsService.addComment(
        selectedReport._id,
        newComment.trim(),
        userId || undefined,
        userName || undefined
      );
      
      // Add the new comment to the list
      setComments([...comments, newCommentData]);
      setNewComment('');
    } catch (err: any) {
      Alert.alert('Lỗi', err.message || 'Không thể thêm bình luận');
    } finally {
      setSubmittingComment(false);
    }
  };

  const communityCategories = ['Tất cả', 'Chờ xử lý', 'Đang xử lý', 'Đã xử lý'];
  const personalCategories = ['Tất cả', 'Bản nháp', 'Chờ xử lý', 'Đang xử lý', 'Đã xử lý'];

  const renderReportItem = ({ item }: { item: ReportItem }) => {
    const isVideo = item.media && item.media.length > 0 && item.media[0].type === 'video';
    const address = item.addressDetail || item.ward || 'Không có địa chỉ';
    
    return (
      <TouchableOpacity
        style={styles.reportCard}
        onPress={() => {
          setSelectedReport(item);
          setShowDetailModal(true);
          fetchComments(item._id || '');
        }}
      >
        <View style={styles.reportImageContainer}>
          {isVideo ? (
            <View style={styles.videoThumbnail}>
              <MaterialIcons name="videocam" size={32} color="#FFFFFF" />
              <View style={styles.videoBadge}>
                <MaterialIcons name="play-circle-filled" size={20} color="#FFFFFF" />
              </View>
            </View>
          ) : (
            item.imageUrl ? (
              <Image 
                source={{ uri: item.imageUrl }} 
                style={styles.reportImage}
              />
            ) : (
              <View style={styles.placeholderImage}>
                <MaterialIcons name="image" size={32} color="#9CA3AF" />
              </View>
            )
          )}
        </View>
        <View style={styles.reportContent}>
          <Text style={styles.reportTitle} numberOfLines={2}>
            {item.title || (item.content ? item.content.substring(0, 50) + (item.content.length > 50 ? '...' : '') : 'Không có tiêu đề')}
          </Text>
          {item.title ? (
            <Text style={styles.reportContentText} numberOfLines={2}>
              {item.content}
            </Text>
          ) : null}
          <Text style={styles.reportAddress} numberOfLines={1}>
            {address}
          </Text>
          <View style={styles.reportFooter}>
            <Text style={styles.reportTime}>{item.displayTime}</Text>
            <Text style={styles.reportStatus}>{item.displayStatus}</Text>
          </View>
        </View>
      </TouchableOpacity>
    );
  };

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

  const filteredReports = bottomIndex === 0 ? communityReports : personalReports;

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
          {loading ? (
            <View style={styles.loadingContainer}>
              <ActivityIndicator size="large" color="#20A957" />
              <Text style={styles.loadingText}>Đang tải...</Text>
            </View>
          ) : error ? (
            <View style={styles.emptyState}>
              <MaterialIcons name="error-outline" size={48} color="#EF4444" />
              <Text style={styles.errorText}>{error}</Text>
              <TouchableOpacity
                style={styles.retryButton}
                onPress={() => fetchReports(false)}
              >
                <Text style={styles.retryButtonText}>Thử lại</Text>
              </TouchableOpacity>
            </View>
          ) : filteredReports.length === 0 ? (
            <View style={styles.emptyState}>
              <MaterialIcons name="inbox" size={48} color="#9CA3AF" />
              <Text style={styles.emptyText}>
                {bottomIndex === 0 
                  ? 'Chưa có phản ánh nào từ cộng đồng.'
                  : 'Các phản ánh của bạn sẽ hiển thị tại đây.'}
              </Text>
            </View>
          ) : (
            <FlatList
              data={filteredReports}
              renderItem={renderReportItem}
              keyExtractor={(item, index) => item._id || `report-${index}`}
              contentContainerStyle={styles.listContent}
              showsVerticalScrollIndicator={true}
              refreshControl={
                <RefreshControl
                  refreshing={refreshing}
                  onRefresh={handleRefresh}
                  colors={['#20A957']}
                  tintColor="#20A957"
                  progressBackgroundColor="#FFFFFF"
                />
              }
            />
          )}
        </View>
      </View>

      {/* Bottom Navigation */}
      <View style={styles.bottomNav}>
        <TouchableOpacity
          style={styles.bottomNavItem}
          onPress={() => {
            setBottomIndex(0);
            setSelectedCategory('Tất cả');
          }}
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
        <View style={styles.fabWrapper}>
          <TouchableOpacity
            style={styles.fab}
            onPress={() => navigation.navigate('CreateReport')}
          >
            <MaterialIcons name="add" size={28} color="#FFFFFF" />
          </TouchableOpacity>
          <Text style={styles.fabLabel}>Tạo phản ánh</Text>
        </View>

        <TouchableOpacity
          style={styles.bottomNavItem}
          onPress={() => {
            setBottomIndex(1);
            setSelectedCategory('Tất cả');
          }}
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

      {/* Report Detail Modal */}
      <Modal
        visible={showDetailModal}
        transparent
        animationType="slide"
        onRequestClose={() => setShowDetailModal(false)}
      >
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            {selectedReport && (
              <>
                {/* Modal Header */}
                <View style={styles.modalHeader}>
                  <Text style={styles.modalTitle}>Chi tiết phản ánh</Text>
                  <TouchableOpacity
                    onPress={() => {
                      setShowDetailModal(false);
                      setSelectedReport(null);
                      setComments([]);
                      setNewComment('');
                    }}
                  >
                    <MaterialIcons name="close" size={24} color="#111827" />
                  </TouchableOpacity>
                </View>

                {/* Modal Body */}
                <ScrollView style={styles.modalBody} showsVerticalScrollIndicator={true}>
                  {/* Report Images/Media */}
                  {selectedReport.media && selectedReport.media.length > 0 && (
                    <ScrollView 
                      horizontal 
                      pagingEnabled 
                      showsHorizontalScrollIndicator={false}
                      style={styles.mediaScrollView}
                    >
                      {selectedReport.media.map((media, index) => (
                        <View key={index} style={styles.mediaItem}>
                          {media.type === 'video' ? (
                            <TouchableOpacity
                              style={styles.videoContainer}
                              onPress={() => setPlayingVideo({ uri: media.uri, index })}
                              activeOpacity={0.8}
                            >
                              <MaterialIcons name="videocam" size={48} color="#FFFFFF" />
                              <View style={styles.videoBadgeLarge}>
                                <MaterialIcons name="play-circle-filled" size={32} color="#FFFFFF" />
                              </View>
                            </TouchableOpacity>
                          ) : (
                            <Image 
                              source={{ uri: media.uri }} 
                              style={styles.mediaImage}
                              resizeMode="cover"
                            />
                          )}
                        </View>
                      ))}
                    </ScrollView>
                  )}

                  {/* Report Content */}
                  <View style={styles.modalReportContent}>
                    <Text style={styles.modalReportTitle}>
                      {selectedReport.title || 'Không có tiêu đề'}
                    </Text>
                    
                    <Text style={styles.modalReportText}>
                      {selectedReport.content}
                    </Text>

                    <View style={styles.modalReportInfo}>
                      <View style={styles.modalInfoRow}>
                        <MaterialIcons name="category" size={18} color="#6B7280" />
                        <Text style={styles.modalInfoText}>{selectedReport.reportType}</Text>
                      </View>
                      <View style={styles.modalInfoRow}>
                        <MaterialIcons name="place" size={18} color="#6B7280" />
                        <Text style={styles.modalInfoText}>
                          {selectedReport.addressDetail || selectedReport.ward || 'Không có địa chỉ'}
                        </Text>
                      </View>
                      <View style={styles.modalInfoRow}>
                        <MaterialIcons name="schedule" size={18} color="#6B7280" />
                        <Text style={styles.modalInfoText}>{selectedReport.displayTime}</Text>
                      </View>
                      <View style={styles.modalInfoRow}>
                        <MaterialIcons name="info" size={18} color="#6B7280" />
                        <Text style={styles.modalInfoText}>{selectedReport.displayStatus}</Text>
                      </View>
                    </View>
                  </View>

                  {/* Comments Section */}
                  <View style={styles.commentsSection}>
                    <Text style={styles.commentsTitle}>
                      Bình luận ({comments.length})
                    </Text>

                    {/* Comments List */}
                    {comments.length === 0 ? (
                      <View style={styles.noComments}>
                        <MaterialIcons name="comment" size={32} color="#9CA3AF" />
                        <Text style={styles.noCommentsText}>Chưa có bình luận nào</Text>
                      </View>
                    ) : (
                      <View style={styles.commentsList}>
                        {comments.map((comment) => (
                          <View key={comment._id} style={styles.commentItem}>
                            <View style={styles.commentHeader}>
                              <View style={styles.commentAvatar}>
                                <MaterialIcons name="account-circle" size={32} color="#20A957" />
                              </View>
                              <View style={styles.commentContent}>
                                <Text style={styles.commentAuthor}>
                                  {comment.userName || 'Người dùng'}
                                </Text>
                                <Text style={styles.commentTime}>
                                  {formatTime(comment.createdAt)}
                                </Text>
                              </View>
                            </View>
                            <Text style={styles.commentText}>{comment.content}</Text>
                          </View>
                        ))}
                      </View>
                    )}
                  </View>
                </ScrollView>

                {/* Comment Input */}
                <View style={styles.commentInputContainer}>
                  <TextInput
                    style={styles.commentInput}
                    placeholder="Viết bình luận..."
                    placeholderTextColor="#9CA3AF"
                    value={newComment}
                    onChangeText={setNewComment}
                    multiline
                    maxLength={500}
                  />
                  <TouchableOpacity
                    style={[
                      styles.commentSendButton,
                      (!newComment.trim() || submittingComment) && styles.commentSendButtonDisabled
                    ]}
                    onPress={handleSubmitComment}
                    disabled={!newComment.trim() || submittingComment}
                  >
                    {submittingComment ? (
                      <ActivityIndicator size="small" color="#FFFFFF" />
                    ) : (
                      <MaterialIcons name="send" size={20} color="#FFFFFF" />
                    )}
                  </TouchableOpacity>
                </View>
              </>
            )}
          </View>
        </View>
      </Modal>

      {/* Video Player Modal */}
      <Modal
        visible={playingVideo !== null}
        transparent
        animationType="fade"
        onRequestClose={() => setPlayingVideo(null)}
      >
        <View style={styles.videoPlayerOverlay}>
          <TouchableOpacity
            style={styles.videoPlayerCloseButton}
            onPress={() => setPlayingVideo(null)}
          >
            <MaterialIcons name="close" size={28} color="#FFFFFF" />
          </TouchableOpacity>
          
          {playingVideo && (
            <View style={styles.videoPlayerContainer}>
              {Platform.OS === 'web' ? (
                // @ts-ignore - HTML video element for web
                <video
                  style={styles.videoPlayer}
                  controls
                  autoPlay
                  playsInline
                  src={playingVideo.uri}
                >
                  Trình duyệt của bạn không hỗ trợ video.
                </video>
              ) : (
                // For native platforms, show a message to use a video player library
                <View style={styles.videoPlayerNative}>
                  <MaterialIcons name="videocam" size={64} color="#FFFFFF" />
                  <Text style={styles.videoPlayerNativeText}>
                    Video: {playingVideo.uri.substring(0, 50)}...
                  </Text>
                  <Text style={styles.videoPlayerNativeHint}>
                    Để phát video trên thiết bị di động, cần cài đặt thư viện video player
                  </Text>
                </View>
              )}
            </View>
          )}
        </View>
      </Modal>
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
  reportImageContainer: {
    width: 100,
    height: 80,
    backgroundColor: '#E5E7EB',
    borderRadius: 8,
    overflow: 'hidden',
  },
  reportImage: {
    width: '100%',
    height: '100%',
    resizeMode: 'cover',
  },
  placeholderImage: {
    width: '100%',
    height: '100%',
    backgroundColor: '#E5E7EB',
    alignItems: 'center',
    justifyContent: 'center',
  },
  videoThumbnail: {
    width: '100%',
    height: '100%',
    backgroundColor: '#1F2937',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
  },
  videoBadge: {
    position: 'absolute',
    bottom: 8,
    right: 8,
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    borderRadius: 12,
    padding: 4,
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
  reportContentText: {
    fontSize: 12,
    color: '#6B7280',
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
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 16,
  },
  loadingText: {
    marginTop: 12,
    fontSize: 14,
    color: '#6B7280',
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
    marginTop: 12,
  },
  errorText: {
    fontSize: 14,
    color: '#EF4444',
    textAlign: 'center',
    marginTop: 12,
    marginBottom: 16,
  },
  retryButton: {
    backgroundColor: '#20A957',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#FFFFFF',
    fontSize: 14,
    fontWeight: '600',
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
  fabWrapper: {
    alignItems: 'center',
    flex: 1,
  },
  fabLabel: {
    marginTop: 6,
    fontSize: 11,
    color: '#20A957',
    fontWeight: '600',
  },
  bottomNav: {
    flexDirection: 'row',
    height: 76,
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
  // Modal styles
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end',
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 20,
    borderTopRightRadius: 20,
    height: Dimensions.get('window').height * 0.67, // 2/3 of screen
    maxHeight: '67%',
    flexDirection: 'column',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#111827',
  },
  modalBody: {
    flex: 1,
  },
  mediaScrollView: {
    maxHeight: 200,
  },
  mediaItem: {
    width: Dimensions.get('window').width,
    height: 200,
  },
  mediaImage: {
    width: '100%',
    height: '100%',
  },
  videoContainer: {
    width: '100%',
    height: '100%',
    backgroundColor: '#1F2937',
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
  },
  videoBadgeLarge: {
    position: 'absolute',
    bottom: 16,
    right: 16,
    backgroundColor: 'rgba(0, 0, 0, 0.6)',
    borderRadius: 20,
    padding: 8,
  },
  modalReportContent: {
    padding: 16,
  },
  modalReportTitle: {
    fontSize: 20,
    fontWeight: '700',
    color: '#111827',
    marginBottom: 12,
  },
  modalReportText: {
    fontSize: 14,
    color: '#374151',
    lineHeight: 20,
    marginBottom: 16,
  },
  modalReportInfo: {
    backgroundColor: '#F9FAFB',
    borderRadius: 8,
    padding: 12,
  },
  modalInfoRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 8,
  },
  modalInfoText: {
    fontSize: 14,
    color: '#6B7280',
    marginLeft: 8,
    flex: 1,
  },
  commentsSection: {
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    marginTop: 16,
  },
  commentsTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 16,
  },
  noComments: {
    alignItems: 'center',
    justifyContent: 'center',
    padding: 32,
  },
  noCommentsText: {
    fontSize: 14,
    color: '#9CA3AF',
    marginTop: 8,
  },
  commentsList: {
    gap: 16,
  },
  commentItem: {
    backgroundColor: '#F9FAFB',
    borderRadius: 8,
    padding: 12,
    marginBottom: 12,
  },
  commentHeader: {
    flexDirection: 'row',
    marginBottom: 8,
  },
  commentAvatar: {
    marginRight: 8,
  },
  commentContent: {
    flex: 1,
  },
  commentAuthor: {
    fontSize: 14,
    fontWeight: '600',
    color: '#111827',
  },
  commentTime: {
    fontSize: 12,
    color: '#9CA3AF',
    marginTop: 2,
  },
  commentText: {
    fontSize: 14,
    color: '#374151',
    lineHeight: 20,
  },
  commentInputContainer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    padding: 16,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB',
    backgroundColor: '#FFFFFF',
  },
  commentInput: {
    flex: 1,
    backgroundColor: '#F9FAFB',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 10,
    maxHeight: 100,
    fontSize: 14,
    color: '#111827',
    marginRight: 8,
  },
  commentSendButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#20A957',
    alignItems: 'center',
    justifyContent: 'center',
  },
  commentSendButtonDisabled: {
    opacity: 0.5,
  },
  // Video Player Modal styles
  videoPlayerOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.95)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  videoPlayerCloseButton: {
    position: 'absolute',
    top: 40,
    right: 20,
    zIndex: 10,
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  videoPlayerContainer: {
    width: '100%',
    height: '100%',
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 20,
  },
  videoPlayer: {
    width: '100%',
    maxWidth: Dimensions.get('window').width,
    height: 'auto',
    maxHeight: Dimensions.get('window').height * 0.7,
    backgroundColor: '#000000',
  },
  videoPlayerNative: {
    width: '100%',
    alignItems: 'center',
    justifyContent: 'center',
    padding: 20,
  },
  videoPlayerNativeText: {
    color: '#FFFFFF',
    fontSize: 14,
    marginTop: 16,
    textAlign: 'center',
  },
  videoPlayerNativeHint: {
    color: '#9CA3AF',
    fontSize: 12,
    marginTop: 8,
    textAlign: 'center',
  },
});

export default ReportScreen;
