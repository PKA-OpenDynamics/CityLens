// Copyright (c) 2025 CityLens Contributors
// Licensed under the MIT License

import { Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { Box } from '@mui/material';
import Dashboard from './pages/Dashboard';
import Login from './pages/Login';
import Sidebar from './components/common/Sidebar';
import Header from './components/common/Header';

function App() {
  const location = useLocation();
  const isLoginPage = location.pathname === '/login';

  if (isLoginPage) {
    return <Login />;
  }

  return (
    <Box sx={{ display: 'flex', minHeight: '100vh', bgcolor: '#FFFFFF' }}>
      <Sidebar />
      
      <Box
        sx={{
          width: '80%',
          marginLeft: '20%',
          minHeight: '100vh',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <Header />
        
        <Box
          component="main"
          sx={{
            flex: 1,
            bgcolor: 'background.default',
            overflow: 'auto',
          }}
        >
          <Routes>
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/map" element={<Dashboard />} />
            <Route path="/reports" element={<Dashboard />} />
            <Route path="/analytics" element={<Dashboard />} />
            <Route path="/users" element={<Dashboard />} />
            <Route path="/settings" element={<Dashboard />} />
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Box>
      </Box>
    </Box>
  );
}

export default App;
