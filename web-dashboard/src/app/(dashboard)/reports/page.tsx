// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

'use client';

import { useState, useEffect, useCallback } from 'react';
import { 
  FileText, AlertCircle, CheckCircle, Clock, RefreshCw, 
  Search, MapPin, MessageCircle, Send, X, 
  ChevronDown, Image as ImageIcon, Eye, XCircle,
  Building2, Trees, Shield, Car, Trash2, Lightbulb, Droplets
} from 'lucide-react';
import { CachedImage } from '@/components/CachedImage';
import { imageCacheService } from '@/lib/image-cache';

// Icon mapping for report types
const REPORT_TYPE_ICONS: Record<string, React.ReactNode> = {
  'infrastructure': <Building2 className="h-5 w-5" />,
  'environment': <Trees className="h-5 w-5" />,
  'security': <Shield className="h-5 w-5" />,
  'traffic': <Car className="h-5 w-5" />,
  'sanitation': <Trash2 className="h-5 w-5" />,
  'lighting': <Lightbulb className="h-5 w-5" />,
  'water': <Droplets className="h-5 w-5" />,
  'other': <FileText className="h-5 w-5" />,
};

const getReportIcon = (type: string) => {
  return REPORT_TYPE_ICONS[type] || <FileText className="h-5 w-5" />;
};
import toast from 'react-hot-toast';
import {
  appReportsApi,
  type AppReport,
  type AppComment,
  type AppReportStats,
  REPORT_TYPES,
  REPORT_STATUSES,
  getReportTypeLabel,
  getStatusLabel,
  formatTimeAgo,
} from '@/lib/app-reports-api';

export default function ReportsPage() {
  // State
  const [reports, setReports] = useState<AppReport[]>([]);
  const [stats, setStats] = useState<AppReportStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  
  // Filters
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [typeFilter, setTypeFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Detail modal
  const [selectedReport, setSelectedReport] = useState<AppReport | null>(null);
  const [showDetailModal, setShowDetailModal] = useState(false);
  const [comments, setComments] = useState<AppComment[]>([]);
  const [loadingComments, setLoadingComments] = useState(false);
  const [newComment, setNewComment] = useState('');
  const [submittingComment, setSubmittingComment] = useState(false);
  
  // Status update modal
  const [showStatusModal, setShowStatusModal] = useState(false);
  const [newStatus, setNewStatus] = useState('');
  const [adminNote, setAdminNote] = useState('');
  const [updatingStatus, setUpdatingStatus] = useState(false);

  // Image viewer
  const [selectedImage, setSelectedImage] = useState<string | null>(null);

  // Fetch data (optimized - load media for display)
  const fetchData = useCallback(async (showToast = false) => {
    try {
      if (showToast) setRefreshing(true);
      
      // Include media but with pagination for performance
      const [reportsRes, statsRes] = await Promise.all([
        appReportsApi.getReports({ limit: 50, include_media: true }),
        appReportsApi.getStats(),
      ]);

      if (reportsRes.success) {
        setReports(reportsRes.data);
        
        // Preload images in background
        const imageUrls = reportsRes.data
          .filter(r => r.media && r.media.length > 0)
          .flatMap(r => r.media.slice(0, 3).map(m => m.uri));
        
        if (imageUrls.length > 0) {
          imageCacheService.preloadImages(imageUrls);
        }
      }
      if (statsRes.success) {
        setStats(statsRes.data);
      }

      if (showToast) toast.success('Đã cập nhật dữ liệu');
    } catch (error) {
      console.error('Error fetching data:', error);
      toast.error('Không thể tải dữ liệu');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, []);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Fetch comments for selected report
  const fetchComments = useCallback(async (reportId: string) => {
    setLoadingComments(true);
    try {
      const response = await appReportsApi.getComments(reportId);
      if (response.success) {
        setComments(response.data);
      }
    } catch (error) {
      console.error('Error fetching comments:', error);
    } finally {
      setLoadingComments(false);
    }
  }, []);

  // Open detail modal
  const openDetailModal = (report: AppReport) => {
    setSelectedReport(report);
    setShowDetailModal(true);
    fetchComments(report._id);
  };

  // Close detail modal
  const closeDetailModal = () => {
    setShowDetailModal(false);
    setSelectedReport(null);
    setComments([]);
    setNewComment('');
  };

  // Submit comment
  const handleSubmitComment = async () => {
    if (!newComment.trim() || !selectedReport) return;
    
    setSubmittingComment(true);
    try {
      const response = await appReportsApi.createComment(
        selectedReport._id,
        newComment,
        'admin',
        'Vũ Đăng Khoa - Quản trị viên'
      );
      
      if (response.success) {
        setComments([...comments, response.data]);
        setNewComment('');
        toast.success('Đã gửi phản hồi');
      }
    } catch (error) {
      toast.error('Không thể gửi phản hồi');
    } finally {
      setSubmittingComment(false);
    }
  };

  // Open status modal
  const openStatusModal = (report: AppReport) => {
    setSelectedReport(report);
    setNewStatus(report.status);
    setAdminNote(report.adminNote || '');
    setShowStatusModal(true);
  };

  // Update status
  const handleUpdateStatus = async () => {
    if (!selectedReport || !newStatus) return;
    
    setUpdatingStatus(true);
    try {
      const token = localStorage.getItem('admin_token') || undefined;
      
      const response = await appReportsApi.updateStatus(
        selectedReport._id,
        newStatus,
        adminNote,
        token
      );
      
      if (response.success) {
        setReports(prev => prev.map(r => 
          r._id === selectedReport._id 
            ? { ...r, status: newStatus as AppReport['status'], adminNote } 
            : r
        ));
        setShowStatusModal(false);
        toast.success('Đã cập nhật trạng thái');
        
        const statsRes = await appReportsApi.getStats();
        if (statsRes.success) {
          setStats(statsRes.data);
        }
      }
    } catch (error) {
      toast.error('Không thể cập nhật trạng thái');
    } finally {
      setUpdatingStatus(false);
    }
  };

  // Filter reports
  const filteredReports = reports.filter(report => {
    if (statusFilter !== 'all' && report.status !== statusFilter) return false;
    if (typeFilter !== 'all' && report.reportType !== typeFilter) return false;
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      return (
        report.title?.toLowerCase().includes(query) ||
        report.content.toLowerCase().includes(query) ||
        report.ward.toLowerCase().includes(query) ||
        report.addressDetail?.toLowerCase().includes(query)
      );
    }
    return true;
  });

  // Get status badge color
  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400';
      case 'processing':
        return 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400';
      case 'resolved':
        return 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400';
      case 'rejected':
        return 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-background">
        <div className="text-center">
          <div className="animate-spin rounded-full h-10 w-10 border-2 border-green-600 border-t-transparent mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Đang tải dữ liệu...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="animate-fade-in space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <FileText className="h-6 w-6 text-green-600 dark:text-green-500" />
            Quản lý Phản ánh
          </h1>
          <p className="text-muted-foreground text-sm mt-1">
            Tiếp nhận và xử lý phản ánh từ người dân qua ứng dụng CityLens
          </p>
        </div>
        <button
          onClick={() => fetchData(true)}
          disabled={refreshing}
          className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
        >
          <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
          Làm mới
        </button>
      </div>

      {/* Stats Overview */}
      <div className="grid gap-4 md:grid-cols-5">
        <div className="rounded-xl border border-border bg-card p-5">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-500/10">
              <FileText className="h-6 w-6 text-blue-500" />
            </div>
            <div>
              <p className="text-2xl font-bold text-foreground">{stats?.total || 0}</p>
              <p className="text-sm text-muted-foreground">Tổng phản ánh</p>
            </div>
          </div>
        </div>
        
        <div className="rounded-xl border border-border bg-card p-5">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-yellow-500/10">
              <Clock className="h-6 w-6 text-yellow-500" />
            </div>
            <div>
              <p className="text-2xl font-bold text-foreground">{stats?.pending || 0}</p>
              <p className="text-sm text-muted-foreground">Chờ xử lý</p>
            </div>
          </div>
        </div>
        
        <div className="rounded-xl border border-border bg-card p-5">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-blue-500/10">
              <AlertCircle className="h-6 w-6 text-blue-500" />
            </div>
            <div>
              <p className="text-2xl font-bold text-foreground">{stats?.processing || 0}</p>
              <p className="text-sm text-muted-foreground">Đang xử lý</p>
            </div>
          </div>
        </div>
        
        <div className="rounded-xl border border-border bg-card p-5">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-green-500/10">
              <CheckCircle className="h-6 w-6 text-green-500" />
            </div>
            <div>
              <p className="text-2xl font-bold text-foreground">{stats?.resolved || 0}</p>
              <p className="text-sm text-muted-foreground">Đã xử lý</p>
            </div>
          </div>
        </div>

        <div className="rounded-xl border border-border bg-card p-5">
          <div className="flex items-center gap-4">
            <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-red-500/10">
              <XCircle className="h-6 w-6 text-red-500" />
            </div>
            <div>
              <p className="text-2xl font-bold text-foreground">{stats?.rejected || 0}</p>
              <p className="text-sm text-muted-foreground">Từ chối</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex flex-wrap gap-4 items-center bg-card rounded-xl border border-border p-4">
        <div className="flex-1 min-w-[200px]">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Tìm kiếm phản ánh..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 rounded-lg border border-border bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
            />
          </div>
        </div>

        <div className="relative">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="appearance-none pl-4 pr-10 py-2 rounded-lg border border-border bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-green-500 cursor-pointer"
          >
            <option value="all">Tất cả trạng thái</option>
            {REPORT_STATUSES.map(status => (
              <option key={status.value} value={status.value}>{status.label}</option>
            ))}
          </select>
          <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
        </div>

        <div className="relative">
          <select
            value={typeFilter}
            onChange={(e) => setTypeFilter(e.target.value)}
            className="appearance-none pl-4 pr-10 py-2 rounded-lg border border-border bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-green-500 cursor-pointer"
          >
            <option value="all">Tất cả loại</option>
            {REPORT_TYPES.map(type => (
              <option key={type.value} value={type.value}>{type.icon} {type.label}</option>
            ))}
          </select>
          <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground pointer-events-none" />
        </div>

        <div className="text-sm text-muted-foreground">
          Hiển thị {filteredReports.length} / {reports.length} phản ánh
        </div>
      </div>

      {/* Reports List */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        {filteredReports.length === 0 ? (
          <div className="p-12 text-center">
            <FileText className="mx-auto h-12 w-12 text-muted-foreground/50" />
            <h3 className="mt-4 text-lg font-semibold text-foreground">Không có phản ánh nào</h3>
            <p className="mt-2 text-muted-foreground">
              {searchQuery || statusFilter !== 'all' || typeFilter !== 'all' 
                ? 'Thử thay đổi bộ lọc để xem thêm kết quả'
                : 'Chưa có phản ánh nào từ người dân'}
            </p>
          </div>
        ) : (
          <div className="divide-y divide-border">
            {filteredReports.map(report => (
              <div 
                key={report._id} 
                className="p-4 hover:bg-muted/50 transition-colors cursor-pointer"
                onClick={() => openDetailModal(report)}
              >
                <div className="flex items-start gap-4">
                  <div className="flex-shrink-0">
                    {report.media && report.media.length > 0 ? (
                      <CachedImage
                        src={report.media[0].uri}
                        alt="Report"
                        className="w-20 h-20 object-cover rounded-lg border border-border"
                        fallbackClassName="w-20 h-20 rounded-lg border border-border"
                        fallbackIcon={<ImageIcon className="h-8 w-8 text-muted-foreground/50" />}
                      />
                    ) : (
                      <div className="w-20 h-20 bg-muted rounded-lg border border-border flex items-center justify-center">
                        <ImageIcon className="h-8 w-8 text-muted-foreground/50" />
                      </div>
                    )}
                  </div>

                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-green-600">{getReportIcon(report.reportType)}</span>
                          <span className="text-sm font-medium text-muted-foreground">
                            {getReportTypeLabel(report.reportType)}
                          </span>
                          <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${getStatusBadgeClass(report.status)}`}>
                            {getStatusLabel(report.status)}
                          </span>
                        </div>
                        <h3 className="font-semibold text-foreground truncate">
                          {report.title || report.content.slice(0, 50) + '...'}
                        </h3>
                        <p className="text-sm text-muted-foreground line-clamp-2 mt-1">
                          {report.content}
                        </p>
                      </div>
                    </div>

                    <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                      <span className="flex items-center gap-1">
                        <MapPin className="h-3 w-3" />
                        {report.ward}{report.addressDetail ? `, ${report.addressDetail}` : ''}
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="h-3 w-3" />
                        {formatTimeAgo(report.createdAt)}
                      </span>
                      {report.media && report.media.length > 0 && (
                        <span className="flex items-center gap-1">
                          <ImageIcon className="h-3 w-3" />
                          {report.media.length} ảnh/video
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="flex-shrink-0 flex items-center gap-2">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        openStatusModal(report);
                      }}
                      className="p-2 rounded-lg hover:bg-muted transition-colors"
                      title="Cập nhật trạng thái"
                    >
                      <AlertCircle className="h-4 w-4 text-muted-foreground" />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        openDetailModal(report);
                      }}
                      className="p-2 rounded-lg hover:bg-muted transition-colors"
                      title="Xem chi tiết"
                    >
                      <Eye className="h-4 w-4 text-muted-foreground" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Detail Modal */}
      {showDetailModal && selectedReport && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-card rounded-xl border border-border w-full max-w-3xl max-h-[90vh] overflow-hidden flex flex-col">
            <div className="flex items-center justify-between p-4 border-b border-border">
              <div className="flex items-center gap-2">
                <span className="text-green-600">{getReportIcon(selectedReport.reportType)}</span>
                <h2 className="text-lg font-semibold text-foreground">Chi tiết phản ánh</h2>
              </div>
              <button onClick={closeDetailModal} className="p-2 hover:bg-muted rounded-lg transition-colors">
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              <div className="flex items-center gap-4 flex-wrap">
                <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusBadgeClass(selectedReport.status)}`}>
                  {getStatusLabel(selectedReport.status)}
                </span>
                <span className="text-sm text-muted-foreground">
                  {getReportTypeLabel(selectedReport.reportType)}
                </span>
                <span className="text-sm text-muted-foreground">
                  {formatTimeAgo(selectedReport.createdAt)}
                </span>
              </div>

              <div>
                <h3 className="text-lg font-semibold text-foreground mb-2">
                  {selectedReport.title || 'Không có tiêu đề'}
                </h3>
                <p className="text-foreground whitespace-pre-wrap">{selectedReport.content}</p>
              </div>

              <div className="flex items-start gap-2 p-3 bg-muted/50 rounded-lg">
                <MapPin className="h-5 w-5 text-green-600 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="font-medium text-foreground">{selectedReport.ward}</p>
                  {selectedReport.addressDetail && (
                    <p className="text-sm text-muted-foreground">{selectedReport.addressDetail}</p>
                  )}
                  {selectedReport.location && (
                    <p className="text-xs text-muted-foreground mt-1">
                      Tọa độ: {selectedReport.location.lat.toFixed(6)}, {selectedReport.location.lng.toFixed(6)}
                    </p>
                  )}
                </div>
              </div>

              {selectedReport.adminNote && (
                <div className="p-3 bg-blue-50 dark:bg-blue-950/20 rounded-lg border border-blue-200 dark:border-blue-800">
                  <p className="text-sm font-medium text-blue-800 dark:text-blue-400 mb-1">Ghi chú của quản trị viên:</p>
                  <p className="text-sm text-foreground">{selectedReport.adminNote}</p>
                </div>
              )}

              {selectedReport.media && selectedReport.media.length > 0 && (
                <div>
                  <h4 className="font-medium text-foreground mb-2">Hình ảnh / Video ({selectedReport.media.length})</h4>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                    {selectedReport.media.map((item, index) => (
                      <div 
                        key={index} 
                        className="relative aspect-square rounded-lg overflow-hidden border border-border cursor-pointer hover:opacity-90 transition-opacity"
                        onClick={() => setSelectedImage(item.uri)}
                      >
                        {item.type === 'image' ? (
                          <CachedImage
                            src={item.uri}
                            alt={`Media ${index + 1}`}
                            className="w-full h-full object-cover"
                            fallbackClassName="w-full h-full"
                            fallbackIcon={<ImageIcon className="h-12 w-12 text-muted-foreground/50" />}
                          />
                        ) : (
                          <video src={item.uri} className="w-full h-full object-cover" />
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div>
                <h4 className="font-medium text-foreground mb-3 flex items-center gap-2">
                  <MessageCircle className="h-4 w-4" />
                  Phản hồi ({comments.length})
                </h4>
                
                {loadingComments ? (
                  <div className="flex items-center justify-center py-4">
                    <div className="animate-spin rounded-full h-6 w-6 border-2 border-green-600 border-t-transparent"></div>
                  </div>
                ) : comments.length === 0 ? (
                  <p className="text-sm text-muted-foreground py-4 text-center">Chưa có phản hồi nào</p>
                ) : (
                  <div className="space-y-3">
                    {comments.map(comment => (
                      <div key={comment._id} className="p-3 bg-muted/50 rounded-lg">
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-sm font-medium text-foreground">{comment.userName}</span>
                          <span className="text-xs text-muted-foreground">{formatTimeAgo(comment.createdAt)}</span>
                        </div>
                        <p className="text-sm text-foreground">{comment.content}</p>
                      </div>
                    ))}
                  </div>
                )}

                <div className="flex gap-2 mt-3">
                  <input
                    type="text"
                    value={newComment}
                    onChange={(e) => setNewComment(e.target.value)}
                    placeholder="Nhập phản hồi..."
                    className="flex-1 px-4 py-2 rounded-lg border border-border bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-green-500"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSubmitComment();
                      }
                    }}
                  />
                  <button
                    onClick={handleSubmitComment}
                    disabled={submittingComment || !newComment.trim()}
                    className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors flex items-center gap-2"
                  >
                    <Send className="h-4 w-4" />
                    Gửi
                  </button>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-between p-4 border-t border-border bg-muted/30">
              <button
                onClick={() => {
                  closeDetailModal();
                  openStatusModal(selectedReport);
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                Cập nhật trạng thái
              </button>
              <button
                onClick={closeDetailModal}
                className="px-4 py-2 border border-border rounded-lg hover:bg-muted transition-colors"
              >
                Đóng
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Status Update Modal */}
      {showStatusModal && selectedReport && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm p-4">
          <div className="bg-card rounded-xl border border-border w-full max-w-md">
            <div className="flex items-center justify-between p-4 border-b border-border">
              <h2 className="text-lg font-semibold text-foreground">Cập nhật trạng thái</h2>
              <button onClick={() => setShowStatusModal(false)} className="p-2 hover:bg-muted rounded-lg transition-colors">
                <X className="h-5 w-5" />
              </button>
            </div>

            <div className="p-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">Trạng thái mới</label>
                <div className="grid grid-cols-2 gap-2">
                  {REPORT_STATUSES.map(status => (
                    <button
                      key={status.value}
                      onClick={() => setNewStatus(status.value)}
                      className={`px-4 py-2 rounded-lg border text-sm font-medium transition-colors ${
                        newStatus === status.value
                          ? 'border-green-500 bg-green-50 dark:bg-green-950/30 text-green-700 dark:text-green-400'
                          : 'border-border hover:bg-muted'
                      }`}
                    >
                      {status.label}
                    </button>
                  ))}
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-foreground mb-2">Ghi chú (tùy chọn)</label>
                <textarea
                  value={adminNote}
                  onChange={(e) => setAdminNote(e.target.value)}
                  placeholder="Nhập ghi chú cho phản ánh này..."
                  rows={3}
                  className="w-full px-4 py-2 rounded-lg border border-border bg-background text-foreground text-sm focus:outline-none focus:ring-2 focus:ring-green-500 resize-none"
                />
              </div>
            </div>

            <div className="flex items-center justify-end gap-2 p-4 border-t border-border">
              <button
                onClick={() => setShowStatusModal(false)}
                className="px-4 py-2 border border-border rounded-lg hover:bg-muted transition-colors"
              >
                Hủy
              </button>
              <button
                onClick={handleUpdateStatus}
                disabled={updatingStatus || newStatus === selectedReport.status}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors"
              >
                {updatingStatus ? 'Đang cập nhật...' : 'Lưu thay đổi'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Image Viewer Modal */}
      {selectedImage && (
        <div 
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 p-4"
          onClick={() => setSelectedImage(null)}
        >
          <button 
            className="absolute top-4 right-4 p-2 text-white hover:bg-white/20 rounded-lg transition-colors"
            onClick={() => setSelectedImage(null)}
          >
            <X className="h-6 w-6" />
          </button>
          <img
            src={selectedImage}
            alt="Full size"
            className="max-w-full max-h-full object-contain"
            onClick={(e) => e.stopPropagation()}
          />
        </div>
      )}
    </div>
  );
}