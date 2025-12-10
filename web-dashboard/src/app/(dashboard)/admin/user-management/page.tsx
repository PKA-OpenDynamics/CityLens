// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

'use client';

import { useState, useEffect } from 'react';
import { 
  Users, Search, Plus, Edit2, Trash2, Shield, RefreshCw, 
  Filter, Download, Eye, UserCheck, UserX, Mail, Phone,
  Calendar, MapPin, Activity
} from 'lucide-react';
import toast from 'react-hot-toast';

// ============================================
// TYPES
// ============================================

interface User {
  id: number;
  email: string;
  full_name: string;
  phone?: string;
  address?: string;
  role: 'admin' | 'staff' | 'user';
  source: 'dashboard' | 'app';
  status: string;  // 'active', 'approved', 'pending', 'suspended', 'inactive'
  is_active: boolean;
  created_at: string;
  last_login?: string;
  avatar?: string;
}

interface UserStats {
  total: number;
  active: number;
  inactive: number;
  dashboard: number;
  app: number;
  by_role: {
    admin?: number;
    staff?: number;
    citizen?: number;
  };
}

// ============================================
// MAIN COMPONENT
// ============================================

export default function UserManagementPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  // Filters
  const [searchQuery, setSearchQuery] = useState('');
  const [roleFilter, setRoleFilter] = useState<string>('all');
  const [sourceFilter, setSourceFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  // Modals
  const [showAddModal, setShowAddModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);

  // Add User Form
  const [newUser, setNewUser] = useState({
    email: '',
    username: '',
    full_name: '',
    phone: '',
    password: '',
    role: 'citizen',
    source: 'dashboard',
    department: '',
    position: '',
  });
  const [addingUser, setAddingUser] = useState(false);

  // Pagination
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(20);

  // ============================================
  // API CALLS
  // ============================================

  const fetchUsers = async (showToast = false) => {
    try {
      if (showToast) setRefreshing(true);

      const token = localStorage.getItem('admin_token');
      const params = new URLSearchParams();
      
      if (roleFilter !== 'all') params.append('role', roleFilter);
      if (sourceFilter !== 'all') params.append('source', sourceFilter);
      if (statusFilter !== 'all') params.append('status', statusFilter);
      if (searchQuery) params.append('search', searchQuery);

      const response = await fetch(
        `http://localhost:8000/api/v1/users?${params.toString()}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error('API Error:', response.status, errorData);
        throw new Error('Failed to fetch users');
      }

      const data = await response.json();
      console.log('Fetched users:', data);
      
      // API trả về array trực tiếp, không phải object
      const usersArray = Array.isArray(data) ? data : (data.users || []);
      setUsers(usersArray);

      if (showToast) toast.success('Đã cập nhật danh sách người dùng');
    } catch (error) {
      console.error('Error fetching users:', error);
      toast.error('Không thể tải danh sách người dùng');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch('http://localhost:8000/api/v1/users/stats', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error('Failed to fetch stats');

      const data = await response.json();
      console.log('Fetched stats:', data);
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const toggleUserStatus = async (userId: number | string, currentStatus: string, userSource: string = 'dashboard') => {
    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch(
        `http://localhost:8000/api/v1/users/${userId}/toggle-status?source=${userSource}`,
        {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) throw new Error('Failed to toggle status');

      toast.success(
        `Đã ${currentStatus === 'active' ? 'vô hiệu hóa' : 'kích hoạt'} người dùng`
      );
      fetchUsers();
      fetchStats();
    } catch (error) {
      console.error('Error toggling status:', error);
      toast.error('Không thể thay đổi trạng thái người dùng');
    }
  };

  const deleteUser = async (userId: number | string, userSource: string = 'dashboard') => {
    if (!confirm('Bạn có chắc muốn xóa người dùng này?')) return;

    try {
      const token = localStorage.getItem('admin_token');
      const response = await fetch(`http://localhost:8000/api/v1/users/${userId}?source=${userSource}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error('Failed to delete user');

      toast.success('Đã xóa người dùng');
      fetchUsers();
      fetchStats();
    } catch (error) {
      console.error('Error deleting user:', error);
      toast.error('Không thể xóa người dùng');
    }
  };

  const createUser = async () => {
    // Validate
    if (!newUser.email || !newUser.full_name || !newUser.password) {
      toast.error('Vui lòng điền đầy đủ thông tin bắt buộc');
      return;
    }

    try {
      setAddingUser(true);
      const token = localStorage.getItem('admin_token');
      
      const response = await fetch('http://localhost:8000/api/v1/users/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...newUser,
          username: newUser.username || newUser.email.split('@')[0],
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Failed to create user');
      }

      toast.success('Đã tạo người dùng mới thành công');
      setShowAddModal(false);
      setNewUser({
        email: '',
        username: '',
        full_name: '',
        phone: '',
        password: '',
        role: 'citizen',
        source: 'dashboard',
        department: '',
        position: '',
      });
      fetchUsers();
      fetchStats();
    } catch (error) {
      console.error('Error creating user:', error);
      toast.error(error instanceof Error ? error.message : 'Không thể tạo người dùng');
    } finally {
      setAddingUser(false);
    }
  };

  // ============================================
  // EFFECTS
  // ============================================

  useEffect(() => {
    fetchUsers();
    fetchStats();
  }, [roleFilter, sourceFilter, statusFilter]);

  useEffect(() => {
    const delayDebounce = setTimeout(() => {
      if (searchQuery) {
        fetchUsers();
      } else if (searchQuery === '') {
        fetchUsers();
      }
    }, 500);

    return () => clearTimeout(delayDebounce);
  }, [searchQuery]);

  // ============================================
  // PAGINATION
  // ============================================

  const filteredUsers = users;
  const totalPages = Math.ceil(filteredUsers.length / itemsPerPage);
  const paginatedUsers = filteredUsers.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  );

  // ============================================
  // RENDER HELPERS
  // ============================================

  const getRoleBadge = (role: string) => {
    const styles = {
      admin: 'bg-red-100 dark:bg-red-900/30 text-red-800 dark:text-red-400',
      staff: 'bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-400',
      user: 'bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-300',
    };

    const labels = {
      admin: 'Quản trị viên',
      staff: 'Nhân viên',
      user: 'Người dùng',
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[role as keyof typeof styles] || styles.user}`}>
        {labels[role as keyof typeof labels] || role}
      </span>
    );
  };

  const getSourceBadge = (source: string) => {
    const styles = {
      dashboard: 'bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-400',
      app: 'bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-400',
    };

    const labels = {
      dashboard: 'Web Dashboard',
      app: 'Mobile App',
    };

    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${styles[source as keyof typeof styles]}`}>
        {labels[source as keyof typeof labels]}
      </span>
    );
  };

  const getStatusBadge = (user: User) => {
    // Check is_active first, then fall back to status string check
    const isActive = user.is_active === true || 
                     user.status === 'active' || 
                     user.status === 'approved';
    
    return isActive ? (
      <span className="flex items-center gap-1 text-green-600 dark:text-green-400 text-sm">
        <UserCheck className="h-4 w-4" />
        Hoạt động
      </span>
    ) : (
      <span className="flex items-center gap-1 text-gray-500 dark:text-gray-400 text-sm">
        <UserX className="h-4 w-4" />
        Vô hiệu hóa
      </span>
    );
  };

  // ============================================
  // RENDER
  // ============================================

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-10 w-10 border-2 border-green-600 border-t-transparent mx-auto"></div>
          <p className="mt-4 text-muted-foreground">Đang tải...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-foreground flex items-center gap-2">
            <Users className="h-6 w-6 text-green-600" />
            Quản lý Người dùng
          </h1>
          <p className="text-muted-foreground text-sm mt-1">
            Quản lý tài khoản và phân quyền người dùng Web Dashboard & Mobile App
          </p>
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={() => fetchUsers(true)}
            disabled={refreshing}
            className="flex items-center gap-2 px-4 py-2 border border-border rounded-lg hover:bg-muted transition-colors"
          >
            <RefreshCw className={`h-4 w-4 ${refreshing ? 'animate-spin' : ''}`} />
            Làm mới
          </button>
          <button
            onClick={() => setShowAddModal(true)}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Plus className="h-4 w-4" />
            Thêm người dùng
          </button>
        </div>
      </div>

      {/* Statistics */}
      {stats && (
        <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-4 mb-6">
          <div className="bg-card rounded-xl border border-border p-4">
            <div className="flex items-center gap-2 text-muted-foreground text-xs mb-1">
              <Users className="h-3 w-3" />
              Tổng số
            </div>
            <div className="text-2xl font-bold text-foreground">{stats.total}</div>
          </div>
          
          <div className="bg-card rounded-xl border border-border p-4">
            <div className="flex items-center gap-2 text-muted-foreground text-xs mb-1">
              <UserCheck className="h-3 w-3" />
              Hoạt động
            </div>
            <div className="text-2xl font-bold text-green-600">{stats.active}</div>
          </div>

          <div className="bg-card rounded-xl border border-border p-4">
            <div className="flex items-center gap-2 text-muted-foreground text-xs mb-1">
              <UserX className="h-3 w-3" />
              Vô hiệu hóa
            </div>
            <div className="text-2xl font-bold text-gray-500">{stats.inactive}</div>
          </div>

          <div className="bg-card rounded-xl border border-border p-4">
            <div className="flex items-center gap-2 text-muted-foreground text-xs mb-1">
              <Shield className="h-3 w-3" />
              Admin
            </div>
            <div className="text-2xl font-bold text-red-600">{stats.by_role?.admin || 0}</div>
          </div>

          <div className="bg-card rounded-xl border border-border p-4">
            <div className="flex items-center gap-2 text-muted-foreground text-xs mb-1">
              <Activity className="h-3 w-3" />
              Staff
            </div>
            <div className="text-2xl font-bold text-blue-600">{stats.by_role?.staff || 0}</div>
          </div>

          <div className="bg-card rounded-xl border border-border p-4">
            <div className="flex items-center gap-2 text-muted-foreground text-xs mb-1">
              <Users className="h-3 w-3" />
              Người dùng
            </div>
            <div className="text-2xl font-bold text-gray-600">{stats.by_role?.citizen || 0}</div>
          </div>

          <div className="bg-card rounded-xl border border-border p-4">
            <div className="flex items-center gap-2 text-purple-600 text-xs mb-1">
              <Activity className="h-3 w-3" />
              Dashboard
            </div>
            <div className="text-2xl font-bold text-purple-600">{stats.dashboard}</div>
          </div>

          <div className="bg-card rounded-xl border border-border p-4">
            <div className="flex items-center gap-2 text-green-600 text-xs mb-1">
              <Activity className="h-3 w-3" />
              Mobile App
            </div>
            <div className="text-2xl font-bold text-green-600">{stats.app}</div>
          </div>
        </div>
      )}

      {/* Filters */}
      <div className="bg-card rounded-xl border border-border p-4 mb-6">
        <div className="flex items-center gap-2 mb-4">
          <Filter className="h-4 w-4 text-muted-foreground" />
          <span className="text-sm font-medium text-foreground">Bộ lọc</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Tìm kiếm theo tên, email..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-9 pr-3 py-2 rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-green-500 text-foreground"
            />
          </div>

          {/* Role Filter */}
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="px-3 py-2 rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-green-500 text-foreground"
          >
            <option value="all">Tất cả vai trò</option>
            <option value="admin">Quản trị viên</option>
            <option value="staff">Nhân viên</option>
            <option value="user">Người dùng</option>
          </select>

          {/* Source Filter */}
          <select
            value={sourceFilter}
            onChange={(e) => setSourceFilter(e.target.value)}
            className="px-3 py-2 rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-green-500 text-foreground"
          >
            <option value="all">Tất cả nguồn</option>
            <option value="dashboard">Web Dashboard</option>
            <option value="app">Mobile App</option>
          </select>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-2 rounded-lg border border-border bg-background focus:outline-none focus:ring-2 focus:ring-green-500 text-foreground"
          >
            <option value="all">Tất cả trạng thái</option>
            <option value="active">Hoạt động</option>
            <option value="inactive">Vô hiệu hóa</option>
          </select>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-card rounded-xl border border-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-muted/50 border-b border-border">
              <tr>
                <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">
                  Người dùng
                </th>
                <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">
                  Liên hệ
                </th>
                <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">
                  Vai trò
                </th>
                <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">
                  Nguồn
                </th>
                <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">
                  Trạng thái
                </th>
                <th className="text-left py-3 px-4 text-xs font-medium text-muted-foreground">
                  Ngày tạo
                </th>
                <th className="text-right py-3 px-4 text-xs font-medium text-muted-foreground">
                  Thao tác
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {paginatedUsers.map((user) => (
                <tr key={user.id} className="hover:bg-muted/30 transition-colors">
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center text-green-600 dark:text-green-400 font-semibold">
                        {user.full_name?.charAt(0).toUpperCase() || 'U'}
                      </div>
                      <div>
                        <div className="font-medium text-foreground">{user.full_name}</div>
                        <div className="text-xs text-muted-foreground">{user.email}</div>
                      </div>
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <div className="space-y-1">
                      {user.phone && (
                        <div className="flex items-center gap-1 text-sm text-muted-foreground">
                          <Phone className="h-3 w-3" />
                          {user.phone}
                        </div>
                      )}
                      {user.address && (
                        <div className="flex items-center gap-1 text-sm text-muted-foreground">
                          <MapPin className="h-3 w-3" />
                          {user.address}
                        </div>
                      )}
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    {getRoleBadge(user.role)}
                  </td>
                  <td className="py-3 px-4">
                    {getSourceBadge(user.source)}
                  </td>
                  <td className="py-3 px-4">
                    {getStatusBadge(user)}
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-1 text-sm text-muted-foreground">
                      <Calendar className="h-3 w-3" />
                      {new Date(user.created_at).toLocaleDateString('vi-VN')}
                    </div>
                    {user.last_login && (
                      <div className="text-xs text-muted-foreground mt-1">
                        Đăng nhập: {new Date(user.last_login).toLocaleDateString('vi-VN')}
                      </div>
                    )}
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => {
                          setSelectedUser(user);
                          setShowEditModal(true);
                        }}
                        className="p-2 hover:bg-muted rounded-lg transition-colors"
                        title="Chỉnh sửa"
                      >
                        <Edit2 className="h-4 w-4 text-blue-600" />
                      </button>
                      <button
                        onClick={() => toggleUserStatus(user.id, user.is_active ? 'active' : 'inactive', user.source)}
                        className="p-2 hover:bg-muted rounded-lg transition-colors"
                        title={user.is_active ? 'Vô hiệu hóa' : 'Kích hoạt'}
                      >
                        {user.is_active ? (
                          <UserX className="h-4 w-4 text-orange-600" />
                        ) : (
                          <UserCheck className="h-4 w-4 text-green-600" />
                        )}
                      </button>
                      <button
                        onClick={() => deleteUser(user.id, user.source)}
                        className="p-2 hover:bg-muted rounded-lg transition-colors"
                        title="Xóa"
                      >
                        <Trash2 className="h-4 w-4 text-red-600" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="flex items-center justify-between p-4 border-t border-border">
            <div className="text-sm text-muted-foreground">
              Hiển thị {(currentPage - 1) * itemsPerPage + 1} - {Math.min(currentPage * itemsPerPage, filteredUsers.length)} / {filteredUsers.length} người dùng
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className="px-3 py-1 border border-border rounded hover:bg-muted disabled:opacity-50 transition-colors"
              >
                Trước
              </button>
              <span className="text-sm text-muted-foreground">
                Trang {currentPage} / {totalPages}
              </span>
              <button
                onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
                className="px-3 py-1 border border-border rounded hover:bg-muted disabled:opacity-50 transition-colors"
              >
                Sau
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Add User Modal */}
      {showAddModal && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div 
            className="absolute inset-0 bg-black/50" 
            onClick={() => setShowAddModal(false)}
          />
          <div className="relative bg-card rounded-xl border border-border shadow-xl w-full max-w-lg mx-4 max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-border">
              <h2 className="text-xl font-bold text-foreground flex items-center gap-2">
                <Plus className="h-5 w-5 text-green-600" />
                Thêm người dùng mới
              </h2>
              <p className="text-sm text-muted-foreground mt-1">
                Tạo tài khoản mới cho Web Dashboard hoặc Mobile App
              </p>
            </div>

            <div className="p-6 space-y-4">
              {/* Source Selection */}
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Loại tài khoản <span className="text-red-500">*</span>
                </label>
                <div className="flex gap-4">
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="source"
                      value="dashboard"
                      checked={newUser.source === 'dashboard'}
                      onChange={(e) => setNewUser({ ...newUser, source: e.target.value, role: 'viewer' })}
                      className="text-green-600"
                    />
                    <span className="text-sm text-foreground">Web Dashboard</span>
                  </label>
                  <label className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="radio"
                      name="source"
                      value="app"
                      checked={newUser.source === 'app'}
                      onChange={(e) => setNewUser({ ...newUser, source: e.target.value, role: 'citizen' })}
                      className="text-green-600"
                    />
                    <span className="text-sm text-foreground">Mobile App</span>
                  </label>
                </div>
              </div>

              {/* Email */}
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Email <span className="text-red-500">*</span>
                </label>
                <input
                  type="email"
                  value={newUser.email}
                  onChange={(e) => setNewUser({ ...newUser, email: e.target.value })}
                  placeholder="user@example.com"
                  className="w-full px-4 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>

              {/* Username */}
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Tên đăng nhập
                </label>
                <input
                  type="text"
                  value={newUser.username}
                  onChange={(e) => setNewUser({ ...newUser, username: e.target.value })}
                  placeholder="username (tự động lấy từ email nếu bỏ trống)"
                  className="w-full px-4 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>

              {/* Full Name */}
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Họ và tên <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  value={newUser.full_name}
                  onChange={(e) => setNewUser({ ...newUser, full_name: e.target.value })}
                  placeholder="Nguyễn Văn A"
                  className="w-full px-4 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>

              {/* Phone */}
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Số điện thoại
                </label>
                <input
                  type="tel"
                  value={newUser.phone}
                  onChange={(e) => setNewUser({ ...newUser, phone: e.target.value })}
                  placeholder="0123456789"
                  className="w-full px-4 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>

              {/* Password */}
              <div>
                <label className="block text-sm font-medium text-foreground mb-2">
                  Mật khẩu <span className="text-red-500">*</span>
                </label>
                <input
                  type="password"
                  value={newUser.password}
                  onChange={(e) => setNewUser({ ...newUser, password: e.target.value })}
                  placeholder="••••••••"
                  className="w-full px-4 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-green-500"
                />
              </div>

              {/* Role (only for Dashboard) */}
              {newUser.source === 'dashboard' && (
                <div>
                  <label className="block text-sm font-medium text-foreground mb-2">
                    Vai trò <span className="text-red-500">*</span>
                  </label>
                  <select
                    value={newUser.role}
                    onChange={(e) => setNewUser({ ...newUser, role: e.target.value })}
                    className="w-full px-4 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-green-500"
                  >
                    <option value="viewer">Người xem (Viewer)</option>
                    <option value="staff">Nhân viên (Staff)</option>
                    <option value="admin">Quản trị viên (Admin)</option>
                  </select>
                </div>
              )}

              {/* Department & Position (only for Dashboard) */}
              {newUser.source === 'dashboard' && (
                <>
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Phòng ban
                    </label>
                    <input
                      type="text"
                      value={newUser.department}
                      onChange={(e) => setNewUser({ ...newUser, department: e.target.value })}
                      placeholder="Phòng Công nghệ"
                      className="w-full px-4 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-green-500"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-foreground mb-2">
                      Chức vụ
                    </label>
                    <input
                      type="text"
                      value={newUser.position}
                      onChange={(e) => setNewUser({ ...newUser, position: e.target.value })}
                      placeholder="Kỹ sư phần mềm"
                      className="w-full px-4 py-2 border border-border rounded-lg bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-green-500"
                    />
                  </div>
                </>
              )}
            </div>

            <div className="p-6 border-t border-border flex items-center justify-end gap-3">
              <button
                onClick={() => setShowAddModal(false)}
                className="px-4 py-2 border border-border rounded-lg hover:bg-muted transition-colors"
              >
                Hủy
              </button>
              <button
                onClick={createUser}
                disabled={addingUser}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 transition-colors flex items-center gap-2"
              >
                {addingUser ? (
                  <>
                    <RefreshCw className="h-4 w-4 animate-spin" />
                    Đang tạo...
                  </>
                ) : (
                  <>
                    <Plus className="h-4 w-4" />
                    Tạo người dùng
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
