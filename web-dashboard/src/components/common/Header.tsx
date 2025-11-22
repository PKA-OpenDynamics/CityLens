// Copyright (c) 2025 CityLens Contributors
// Licensed under the MIT License

import {
  Box,
  IconButton,
  Badge,
  Avatar,
  Menu,
  MenuItem,
  Typography,
  Divider,
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  AccountCircle,
  Logout,
} from '@mui/icons-material';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Header() {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const navigate = useNavigate();

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    navigate('/login');
  };

  return (
    <Box
      sx={{
        height: 64,
        borderBottom: '1px solid',
        borderColor: 'divider',
        bgcolor: 'background.paper',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'flex-end',
        px: 3,
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <IconButton size="large" color="inherit">
          <Badge badgeContent={4} sx={{
            '& .MuiBadge-badge': {
              backgroundColor: '#6B7280',
              color: 'white',
            }
          }}>
            <NotificationsIcon />
          </Badge>
        </IconButton>

        <IconButton onClick={handleMenu} sx={{ p: 0.5 }}>
          <Avatar sx={{ width: 36, height: 36, bgcolor: '#374151', color: 'white' }}>
            A
          </Avatar>
        </IconButton>

        <Menu
          anchorEl={anchorEl}
          open={Boolean(anchorEl)}
          onClose={handleClose}
          transformOrigin={{ horizontal: 'right', vertical: 'top' }}
          anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
          PaperProps={{
            sx: { width: 220, mt: 1.5 },
          }}
        >
          <Box sx={{ px: 2, py: 1.5 }}>
            <Typography variant="subtitle2" fontWeight={600}>
              Quản trị viên
            </Typography>
            <Typography variant="caption" color="text.secondary">
              admin@citylens.vn
            </Typography>
          </Box>
          <Divider />
          <MenuItem onClick={handleClose}>
            <AccountCircle sx={{ mr: 1.5, fontSize: 20 }} />
            Tài khoản
          </MenuItem>
          <MenuItem onClick={handleLogout}>
            <Logout sx={{ mr: 1.5, fontSize: 20 }} />
            Đăng xuất
          </MenuItem>
        </Menu>
      </Box>
    </Box>
  );
}
