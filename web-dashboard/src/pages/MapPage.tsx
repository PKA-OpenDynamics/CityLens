// Copyright (c) 2025 CityLens Contributors
// Licensed under the MIT License

import { Box, Container, Typography, Paper } from '@mui/material';

export default function MapPage() {
  return (
    <Box sx={{ p: 4, maxWidth: '100%', mx: 'auto' }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5 }}>
          Bản đồ sự kiện
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Theo dõi các sự kiện và báo cáo trên bản đồ thời gian thực
        </Typography>
      </Box>

      <Paper
        sx={{
          height: 'calc(100vh - 200px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          bgcolor: 'background.paper',
          border: 1,
          borderColor: 'divider',
        }}
      >
        <Box sx={{ textAlign: 'center' }}>
          <Typography variant="h6" color="text.secondary" gutterBottom>
            Bản đồ Mapbox
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Tích hợp Mapbox GL JS sẽ được thêm vào đây
          </Typography>
        </Box>
      </Paper>
    </Box>
  );
}
