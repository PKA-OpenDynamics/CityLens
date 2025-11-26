// Copyright (c) 2025 CityLens Contributors
// Licensed under the MIT License

import { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Grid,
  Paper,
  Chip,
  Stack,
  Alert,
  CircularProgress,
} from '@mui/material';
import {
  Warning,
  Sensors,
  AccountBalance,
  TrendingUp,
} from '@mui/icons-material';
// Use simple version without clustering to avoid compatibility issues
import CityMap from '../components/maps/CityMapSimple';
import MapFilters, { MapFilterState } from '../components/maps/MapFilters';

interface MapMarker {
  id: string;
  type: 'report' | 'sensor' | 'facility';
  coordinates: [number, number]; // [lat, lng] for Leaflet
  title: string;
  description?: string;
  severity?: 'low' | 'medium' | 'high';
}

export default function MapPage() {
  const [filters, setFilters] = useState<MapFilterState>({
    showReports: true,
    showSensors: true,
    showFacilities: true,
    severity: ['low', 'medium', 'high'],
    timeRange: 24,
    district: 'all',
  });
  const [markers, setMarkers] = useState<MapMarker[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalReports: 0,
    activeSensors: 0,
    facilities: 0,
    recentActivity: 0,
  });

  // Mock data - Replace with actual API calls
  useEffect(() => {
    const fetchMapData = async () => {
      setLoading(true);
      
      // Simulate API call
      await new Promise((resolve) => setTimeout(resolve, 800));

      // Generate sample markers using data generator
      const { generateAllMarkers, getMarkerStats } = await import('../utils/mapDataGenerator');
      const sampleMarkers = generateAllMarkers(50, 100, 30);

      setMarkers(sampleMarkers);
      
      // Calculate real stats from generated data
      const stats = getMarkerStats(sampleMarkers);
      setStats({
        totalReports: stats.reports,
        activeSensors: stats.sensors,
        facilities: stats.facilities,
        recentActivity: stats.highSeverity + Math.floor(Math.random() * 10),
      });
      setLoading(false);
    };

    fetchMapData();
  }, [filters]);

  // Filter markers based on filters
  const filteredMarkers = markers.filter((marker) => {
    if (marker.type === 'report' && !filters.showReports) return false;
    if (marker.type === 'sensor' && !filters.showSensors) return false;
    if (marker.type === 'facility' && !filters.showFacilities) return false;
    if (marker.severity && !filters.severity.includes(marker.severity)) return false;
    return true;
  });

  const handleMarkerClick = (marker: MapMarker) => {
    console.log('Marker clicked:', marker);
    // Handle marker click - open dialog, show details, etc.
  };

  return (
    <Box sx={{ p: 3, height: 'calc(100vh - 64px)' }}>
      {/* Header */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5 }}>
          Bản đồ sự kiện thành phố
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Theo dõi các sự kiện, báo cáo và cảm biến trên bản đồ thời gian thực
        </Typography>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              alignItems: 'center',
              gap: 2,
            }}
          >
            <Box
              sx={{
                width: 48,
                height: 48,
                borderRadius: 2,
                bgcolor: 'error.light',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Warning sx={{ color: 'error.dark' }} />
            </Box>
            <Box>
              <Typography variant="h5" fontWeight={700}>
                {stats.totalReports}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Báo cáo
              </Typography>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              alignItems: 'center',
              gap: 2,
            }}
          >
            <Box
              sx={{
                width: 48,
                height: 48,
                borderRadius: 2,
                bgcolor: 'info.light',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <Sensors sx={{ color: 'info.dark' }} />
            </Box>
            <Box>
              <Typography variant="h5" fontWeight={700}>
                {stats.activeSensors}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Cảm biến hoạt động
              </Typography>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              alignItems: 'center',
              gap: 2,
            }}
          >
            <Box
              sx={{
                width: 48,
                height: 48,
                borderRadius: 2,
                bgcolor: 'secondary.light',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <AccountBalance sx={{ color: 'secondary.dark' }} />
            </Box>
            <Box>
              <Typography variant="h5" fontWeight={700}>
                {stats.facilities}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Cơ sở hạ tầng
              </Typography>
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Paper
            sx={{
              p: 2,
              display: 'flex',
              alignItems: 'center',
              gap: 2,
            }}
          >
            <Box
              sx={{
                width: 48,
                height: 48,
                borderRadius: 2,
                bgcolor: 'success.light',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <TrendingUp sx={{ color: 'success.dark' }} />
            </Box>
            <Box>
              <Typography variant="h5" fontWeight={700}>
                +{stats.recentActivity}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Hoạt động gần đây
              </Typography>
            </Box>
          </Paper>
        </Grid>
      </Grid>

      {/* Map and Filters */}
      <Grid container spacing={2} sx={{ height: 'calc(100% - 200px)' }}>
        <Grid item xs={12} md={9}>
          <Paper
            sx={{
              height: '100%',
              position: 'relative',
              overflow: 'hidden',
            }}
          >
            {loading ? (
              <Box
                sx={{
                  height: '100%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <CircularProgress />
              </Box>
            ) : (
              <CityMap
                center={[21.0285, 105.8542]}
                zoom={12}
                markers={filteredMarkers}
                onMarkerClick={handleMarkerClick}
              />
            )}
          </Paper>
        </Grid>

        <Grid item xs={12} md={3}>
          <MapFilters onFilterChange={setFilters} />
        </Grid>
      </Grid>
    </Box>
  );
}
