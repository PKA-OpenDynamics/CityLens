// Copyright (c) 2025 CityLens Contributors
// Licensed under the MIT License

import {
  Box,
  Paper,
  Typography,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Divider,
  Slider,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import { useState } from 'react';

interface MapFiltersProps {
  onFilterChange?: (filters: MapFilterState) => void;
}

export interface MapFilterState {
  showReports: boolean;
  showSensors: boolean;
  showFacilities: boolean;
  severity: string[];
  timeRange: number;
  district: string;
}

export default function MapFilters({ onFilterChange }: MapFiltersProps) {
  const [filters, setFilters] = useState<MapFilterState>({
    showReports: true,
    showSensors: true,
    showFacilities: true,
    severity: ['low', 'medium', 'high'],
    timeRange: 24,
    district: 'all',
  });

  const handleFilterChange = (key: keyof MapFilterState, value: any) => {
    const newFilters = { ...filters, [key]: value };
    setFilters(newFilters);
    onFilterChange?.(newFilters);
  };

  const handleSeverityChange = (severity: string) => {
    const newSeverity = filters.severity.includes(severity)
      ? filters.severity.filter((s) => s !== severity)
      : [...filters.severity, severity];
    handleFilterChange('severity', newSeverity);
  };

  return (
    <Paper
      sx={{
        p: 3,
        height: '100%',
        overflow: 'auto',
      }}
    >
      <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
        Bộ lọc bản đồ
      </Typography>

      {/* Layer visibility */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
          Hiển thị lớp dữ liệu
        </Typography>
        <FormGroup>
          <FormControlLabel
            control={
              <Checkbox
                checked={filters.showReports}
                onChange={(e) => handleFilterChange('showReports', e.target.checked)}
              />
            }
            label="Báo cáo từ dân"
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={filters.showSensors}
                onChange={(e) => handleFilterChange('showSensors', e.target.checked)}
              />
            }
            label="Cảm biến IoT"
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={filters.showFacilities}
                onChange={(e) => handleFilterChange('showFacilities', e.target.checked)}
              />
            }
            label="Cơ sở hạ tầng"
          />
        </FormGroup>
      </Box>

      <Divider sx={{ my: 2 }} />

      {/* Severity filter */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
          Mức độ nghiêm trọng
        </Typography>
        <FormGroup>
          <FormControlLabel
            control={
              <Checkbox
                checked={filters.severity.includes('high')}
                onChange={() => handleSeverityChange('high')}
                sx={{
                  color: '#f44336',
                  '&.Mui-checked': { color: '#f44336' },
                }}
              />
            }
            label="Khẩn cấp"
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={filters.severity.includes('medium')}
                onChange={() => handleSeverityChange('medium')}
                sx={{
                  color: '#ff9800',
                  '&.Mui-checked': { color: '#ff9800' },
                }}
              />
            }
            label="Trung bình"
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={filters.severity.includes('low')}
                onChange={() => handleSeverityChange('low')}
                sx={{
                  color: '#4caf50',
                  '&.Mui-checked': { color: '#4caf50' },
                }}
              />
            }
            label="Thấp"
          />
        </FormGroup>
      </Box>

      <Divider sx={{ my: 2 }} />

      {/* Time range */}
      <Box sx={{ mb: 3 }}>
        <Typography variant="subtitle2" sx={{ mb: 1, fontWeight: 600 }}>
          Khoảng thời gian: {filters.timeRange}h
        </Typography>
        <Slider
          value={filters.timeRange}
          onChange={(_, value) => handleFilterChange('timeRange', value)}
          min={1}
          max={168}
          marks={[
            { value: 1, label: '1h' },
            { value: 24, label: '24h' },
            { value: 168, label: '7d' },
          ]}
          valueLabelDisplay="auto"
        />
      </Box>

      <Divider sx={{ my: 2 }} />

      {/* District filter */}
      <Box sx={{ mb: 3 }}>
        <FormControl fullWidth size="small">
          <InputLabel>Quận/Huyện</InputLabel>
          <Select
            value={filters.district}
            label="Quận/Huyện"
            onChange={(e) => handleFilterChange('district', e.target.value)}
          >
            <MenuItem value="all">Tất cả</MenuItem>
            <MenuItem value="q1">Quận 1</MenuItem>
            <MenuItem value="q2">Quận 2</MenuItem>
            <MenuItem value="q3">Quận 3</MenuItem>
            <MenuItem value="q4">Quận 4</MenuItem>
            <MenuItem value="q5">Quận 5</MenuItem>
            <MenuItem value="q6">Quận 6</MenuItem>
            <MenuItem value="q7">Quận 7</MenuItem>
            <MenuItem value="q8">Quận 8</MenuItem>
            <MenuItem value="q9">Quận 9</MenuItem>
            <MenuItem value="q10">Quận 10</MenuItem>
            <MenuItem value="q11">Quận 11</MenuItem>
            <MenuItem value="q12">Quận 12</MenuItem>
            <MenuItem value="thu-duc">Thủ Đức</MenuItem>
            <MenuItem value="binh-tan">Bình Tân</MenuItem>
            <MenuItem value="binh-thanh">Bình Thạnh</MenuItem>
            <MenuItem value="go-vap">Gò Vấp</MenuItem>
            <MenuItem value="phu-nhuan">Phú Nhuận</MenuItem>
            <MenuItem value="tan-binh">Tân Bình</MenuItem>
            <MenuItem value="tan-phu">Tân Phú</MenuItem>
          </Select>
        </FormControl>
      </Box>
    </Paper>
  );
}

