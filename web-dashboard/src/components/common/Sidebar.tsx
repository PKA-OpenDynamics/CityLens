// Copyright (c) 2025 CityLens Contributors
// Licensed under the MIT License

import {
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Box,
  Typography,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Map as MapIcon,
  Report as ReportIcon,
  BarChart as AnalyticsIcon,
  Settings as SettingsIcon,
  People as PeopleIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';

const menuItems = [
  { text: 'Tổng quan', icon: <DashboardIcon />, path: '/dashboard' },
  { text: 'Bản đồ', icon: <MapIcon />, path: '/map' },
  { text: 'Báo cáo', icon: <ReportIcon />, path: '/reports' },
  { text: 'Phân tích', icon: <AnalyticsIcon />, path: '/analytics' },
  { text: 'Người dùng', icon: <PeopleIcon />, path: '/users' },
  { text: 'Cài đặt', icon: <SettingsIcon />, path: '/settings' },
];

export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();

  return (
    <Box
      sx={{
        width: '20%',
        height: '100vh',
        position: 'fixed',
        left: 0,
        top: 0,
        borderRight: '1px solid',
        borderColor: 'divider',
        bgcolor: '#FAFAFA',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <Box sx={{ p: 3, borderBottom: 1, borderColor: 'divider' }}>
        <Typography variant="h5" sx={{ fontWeight: 700, letterSpacing: '-0.02em', mb: 0.5 }}>
          CityLens
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Quản lý thành phố
        </Typography>
      </Box>

      <List sx={{ px: 2, py: 2, flex: 1, overflow: 'auto' }}>
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <ListItem key={item.text} disablePadding sx={{ mb: 0.5 }}>
              <ListItemButton
                onClick={() => navigate(item.path)}
                sx={{
                  borderRadius: 1,
                  bgcolor: isActive ? '#F3F4F6' : 'transparent',
                  color: 'text.primary',
                  border: isActive ? '1px solid #D1D5DB' : '1px solid transparent',
                  '&:hover': {
                    bgcolor: '#F9FAFB',
                  },
                  '& .MuiListItemIcon-root': {
                    color: 'text.secondary',
                  },
                }}
              >
                <ListItemIcon sx={{ minWidth: 40 }}>
                  {item.icon}
                </ListItemIcon>
                <ListItemText
                  primary={item.text}
                  primaryTypographyProps={{
                    fontSize: '0.875rem',
                    fontWeight: isActive ? 600 : 500,
                  }}
                />
              </ListItemButton>
            </ListItem>
          );
        })}
      </List>

      <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
        <Typography variant="caption" color="text.secondary">
          © 2025 CityLens
        </Typography>
      </Box>
    </Box>
  );
}
