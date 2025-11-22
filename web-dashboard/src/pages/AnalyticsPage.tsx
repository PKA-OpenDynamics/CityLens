// Copyright (c) 2025 CityLens Contributors
// Licensed under the MIT License

import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  LinearProgress,
} from '@mui/material';
import {
  TrendingUp,
  ShowChart,
  BarChart as BarChartIcon,
} from '@mui/icons-material';

export default function AnalyticsPage() {
  return (
    <Box sx={{ p: 4, maxWidth: '100%', mx: 'auto' }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5 }}>
          Phân tích dữ liệu
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Thống kê và phân tích các chỉ số quan trọng
        </Typography>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12} lg={8}>
          <Paper
            sx={{
              p: 3,
              height: 400,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <BarChartIcon sx={{ fontSize: 60, color: 'text.secondary', mb: 2 }} />
            <Typography variant="h6" color="text.secondary" gutterBottom>
              Biểu đồ thống kê
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Tích hợp Recharts sẽ được thêm vào đây
            </Typography>
          </Paper>
        </Grid>

        <Grid item xs={12} lg={4}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <TrendingUp color="success" />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Xu hướng tăng trưởng
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="body2">Người dùng mới</Typography>
                    <Typography variant="body2" fontWeight={600}>
                      +24%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={24}
                    sx={{ height: 6, borderRadius: 1 }}
                    color="success"
                  />
                </Box>
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="body2">Báo cáo mới</Typography>
                    <Typography variant="body2" fontWeight={600}>
                      +18%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={18}
                    sx={{ height: 6, borderRadius: 1 }}
                    color="primary"
                  />
                </Box>
                <Box>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                    <Typography variant="body2">Tương tác</Typography>
                    <Typography variant="body2" fontWeight={600}>
                      +32%
                    </Typography>
                  </Box>
                  <LinearProgress
                    variant="determinate"
                    value={32}
                    sx={{ height: 6, borderRadius: 1 }}
                    color="success"
                  />
                </Box>
              </Box>
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
                <ShowChart color="info" />
                <Typography variant="h6" sx={{ fontWeight: 600 }}>
                  Hiệu suất
                </Typography>
              </Box>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Thời gian phản hồi trung bình
                  </Typography>
                  <Typography variant="h5" fontWeight={700}>
                    2.4 giờ
                  </Typography>
                </Box>
                <Box>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    Tỷ lệ giải quyết
                  </Typography>
                  <Typography variant="h5" fontWeight={700}>
                    87%
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}
