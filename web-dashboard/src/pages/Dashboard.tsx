// Copyright (c) 2025 CityLens Contributors
// Licensed under the MIT License

import {
  Box,
  Grid,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  LinearProgress,
} from '@mui/material';
import {
  Report as ReportIcon,
  PendingActions,
  Event as EventIcon,
  People as PeopleIcon,
} from '@mui/icons-material';
import { useEffect, useState } from 'react';
import StatCard from '@/components/common/StatCard';
import { reportService } from '@/services/reports';
import { Report } from '@/types/api';

export default function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalReports: 0,
    pendingReports: 0,
    activeIncidents: 0,
    activeUsers: 0,
  });
  const [recentReports, setRecentReports] = useState<Report[]>([]);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const reports = await reportService.getReports({ limit: 5 });
      const statistics = await reportService.getStatistics();

      setRecentReports(reports);
      setStats({
        totalReports: statistics.total,
        pendingReports: statistics.pending,
        activeIncidents: statistics.active_incidents,
        activeUsers: statistics.active_users,
      });
    } catch (error) {
      console.error('Lỗi tải dữ liệu:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusText = (status: string) => {
    const texts: Record<string, string> = {
      cho_xac_nhan: 'Chờ xác nhận',
      da_xac_nhan: 'Đã xác nhận',
      tu_choi: 'Từ chối',
      da_giai_quyet: 'Đã giải quyết',
    };
    return texts[status] || status;
  };

  return (
    <Box sx={{ p: 4, maxWidth: '100%', mx: 'auto' }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 1 }}>
          Tổng quan
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Thống kê và hoạt động hệ thống
        </Typography>
      </Box>

      <Grid container spacing={2.5}>
        <Grid item xs={12} sm={6} lg={3}>
          <StatCard
            title="Tổng báo cáo"
            value={stats.totalReports.toLocaleString()}
            icon={<ReportIcon sx={{ fontSize: 24 }} />}
            trend={{ value: 12.5, isPositive: true }}
            loading={loading}
          />
        </Grid>

        <Grid item xs={12} sm={6} lg={3}>
          <StatCard
            title="Chờ xác nhận"
            value={stats.pendingReports}
            icon={<PendingActions sx={{ fontSize: 24 }} />}
            trend={{ value: 5.2, isPositive: false }}
            loading={loading}
          />
        </Grid>

        <Grid item xs={12} sm={6} lg={3}>
          <StatCard
            title="Đang xử lý"
            value={stats.activeIncidents}
            icon={<EventIcon sx={{ fontSize: 24 }} />}
            loading={loading}
          />
        </Grid>

        <Grid item xs={12} sm={6} lg={3}>
          <StatCard
            title="Người dùng"
            value={stats.activeUsers.toLocaleString()}
            icon={<PeopleIcon sx={{ fontSize: 24 }} />}
            trend={{ value: 8.1, isPositive: true }}
            loading={loading}
          />
        </Grid>

        <Grid item xs={12} lg={8}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
              Hoạt động gần đây
            </Typography>

            {loading ? (
              <LinearProgress sx={{ bgcolor: '#F3F4F6', '& .MuiLinearProgress-bar': { bgcolor: '#9CA3AF' } }} />
            ) : (
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Tiêu đề</TableCell>
                      <TableCell>Loại</TableCell>
                      <TableCell>Khu vực</TableCell>
                      <TableCell>Trạng thái</TableCell>
                      <TableCell>Thời gian</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {recentReports.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={5} align="center" sx={{ py: 6 }}>
                          <Typography color="text.secondary" variant="body2">
                            Chưa có dữ liệu
                          </Typography>
                        </TableCell>
                      </TableRow>
                    ) : (
                      recentReports.map((report) => (
                        <TableRow key={report.id} sx={{ '&:hover': { bgcolor: '#F9FAFB' } }}>
                          <TableCell sx={{ fontWeight: 500 }}>{report.title}</TableCell>
                          <TableCell>
                            <Chip
                              label={report.incident_type}
                              size="small"
                              variant="outlined"
                            />
                          </TableCell>
                          <TableCell>{report.district || 'N/A'}</TableCell>
                          <TableCell>
                            <Chip
                              label={getStatusText(report.status)}
                              size="small"
                              variant="outlined"
                            />
                          </TableCell>
                          <TableCell>
                            {new Date(report.created_at).toLocaleDateString('vi-VN')}
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </TableContainer>
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Paper sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" sx={{ fontWeight: 600, mb: 3 }}>
              Thống kê theo loại
            </Typography>
            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 3 }}>
              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2" color="text.secondary">Ngập nước</Typography>
                  <Typography variant="body2" fontWeight={600}>65%</Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={65} 
                  sx={{ 
                    height: 6, 
                    borderRadius: 1,
                    bgcolor: '#F3F4F6',
                    '& .MuiLinearProgress-bar': { bgcolor: '#6B7280' }
                  }} 
                />
              </Box>
              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2" color="text.secondary">Kẹt xe</Typography>
                  <Typography variant="body2" fontWeight={600}>45%</Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={45} 
                  sx={{ 
                    height: 6, 
                    borderRadius: 1,
                    bgcolor: '#F3F4F6',
                    '& .MuiLinearProgress-bar': { bgcolor: '#9CA3AF' }
                  }} 
                />
              </Box>
              <Box>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2" color="text.secondary">Chất lượng không khí</Typography>
                  <Typography variant="body2" fontWeight={600}>30%</Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={30} 
                  sx={{ 
                    height: 6, 
                    borderRadius: 1,
                    bgcolor: '#F3F4F6',
                    '& .MuiLinearProgress-bar': { bgcolor: '#D1D5DB' }
                  }} 
                />
              </Box>

              {stats.pendingReports > 0 && (
                <Box sx={{ mt: 2, p: 2, bgcolor: '#F9FAFB', borderRadius: 1, border: '1px solid #E5E7EB' }}>
                  <Typography variant="body2" fontWeight={600} sx={{ mb: 0.5 }}>
                    Cần xử lý
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {stats.pendingReports} báo cáo đang chờ xác nhận
                  </Typography>
                </Box>
              )}
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
}
