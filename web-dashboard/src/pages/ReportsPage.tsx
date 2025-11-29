// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

import {
  Box,
  Paper,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  IconButton,
  TextField,
  InputAdornment,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Search as SearchIcon,
  Visibility,
  Edit,
  Delete,
} from '@mui/icons-material';
import { useEffect, useState } from 'react';
import { reportService } from '@/services/reports';
import { Report } from '@/types/api';

export default function ReportsPage() {
  const [reports, setReports] = useState<Report[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [currentTab, setCurrentTab] = useState(0);

  useEffect(() => {
    loadReports();
  }, [currentTab]);

  const loadReports = async () => {
    try {
      setLoading(true);
      const statusMap = ['', 'cho_xac_nhan', 'da_xac_nhan', 'da_giai_quyet'];
      const data = await reportService.getReports({
        status: statusMap[currentTab],
        limit: 50,
      });
      setReports(data);
    } catch (error) {
      console.error('Lỗi tải báo cáo:', error);
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

  const filteredReports = reports.filter(
    (report) =>
      report.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      (report.description && report.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <Box sx={{ p: 4, maxWidth: '100%', mx: 'auto' }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5 }}>
          Quản lý báo cáo
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Xem và quản lý các báo cáo từ người dân
        </Typography>
      </Box>

      <Paper sx={{ mb: 3 }}>
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
          <TextField
            fullWidth
            placeholder="Tìm kiếm báo cáo..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
        </Box>

        <Tabs
          value={currentTab}
          onChange={(_, newValue) => setCurrentTab(newValue)}
          sx={{ borderBottom: 1, borderColor: 'divider', px: 2 }}
        >
          <Tab label="Tất cả" />
          <Tab label="Chờ xác nhận" />
          <Tab label="Đã xác nhận" />
          <Tab label="Đã giải quyết" />
        </Tabs>

        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell sx={{ fontWeight: 600 }}>Tiêu đề</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Loại sự kiện</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Địa điểm</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Trạng thái</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Ngày tạo</TableCell>
                <TableCell sx={{ fontWeight: 600 }}>Hành động</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                    <Typography color="text.secondary">Đang tải...</Typography>
                  </TableCell>
                </TableRow>
              ) : filteredReports.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center" sx={{ py: 4 }}>
                    <Typography color="text.secondary">
                      Không có báo cáo nào
                    </Typography>
                  </TableCell>
                </TableRow>
              ) : (
                filteredReports.map((report) => (
                  <TableRow key={report.id} hover>
                    <TableCell>{report.title}</TableCell>
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
                    <TableCell>
                      <IconButton size="small">
                        <Visibility fontSize="small" />
                      </IconButton>
                      <IconButton size="small">
                        <Edit fontSize="small" />
                      </IconButton>
                      <IconButton size="small">
                        <Delete fontSize="small" />
                      </IconButton>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Box>
  );
}
