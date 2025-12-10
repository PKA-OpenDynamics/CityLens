// Copyright (c) 2025 CityLens Contributors
// Licensed under the GNU General Public License v3.0 (GPL-3.0)

'use client';

import { useState, useEffect } from 'react';
import { 
  Users, 
  UserCheck,
  UserX,
  Shield,
  Clock,
  CheckCircle,
  XCircle,
  Search,
  Filter
} from 'lucide-react';
import { adminService } from '@/lib/admin-service';
import toast from 'react-hot-toast';
import { cn } from '@/lib/utils';

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  status: string;
  phone?: string;
  department?: string;
  position?: string;
  created_at: string;
}

const roleLabels: Record<string, string> = {
  super_admin: 'Super Admin',
  admin: 'Admin',
  manager: 'Quản lý',
  analyst: 'Phân tích viên',
  viewer: 'Người xem'
};

const roleColors: Record<string, string> = {
  super_admin: 'bg-purple-100 text-purple-800',
  admin: 'bg-blue-100 text-blue-800',
  manager: 'bg-green-100 text-green-800',
  analyst: 'bg-yellow-100 text-yellow-800',
  viewer: 'bg-gray-100 text-gray-800'
};

const statusColors: Record<string, string> = {
  approved: 'bg-green-100 text-green-800',
  pending: 'bg-yellow-100 text-yellow-800',
  suspended: 'bg-red-100 text-red-800',
  rejected: 'bg-gray-100 text-gray-800'
};

export default function AdminUsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [filteredUsers, setFilteredUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [roleFilter, setRoleFilter] = useState<string>('all');
  const [stats, setStats] = useState<any>(null);

  useEffect(() => {
    fetchUsers();
    fetchStats();
  }, []);

  useEffect(() => {
    filterUsers();
  }, [users, searchQuery, statusFilter, roleFilter]);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      const data = await adminService.getAllUsers();
      setUsers(data);
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Không thể tải danh sách người dùng');
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const data = await adminService.getUserStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    }
  };

  const filterUsers = () => {
    let filtered = users;

    if (searchQuery) {
      filtered = filtered.filter(user => 
        user.email.toLowerCase().includes(searchQuery.toLowerCase()) ||
        user.full_name.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    if (statusFilter !== 'all') {
      filtered = filtered.filter(user => user.status === statusFilter);
    }

    if (roleFilter !== 'all') {
      filtered = filtered.filter(user => user.role === roleFilter);
    }

    setFilteredUsers(filtered);
  };

  const handleApprove = async (userId: string, approved: boolean) => {
    try {
      await adminService.approveUser(userId, approved);
      toast.success(approved ? 'Đã phê duyệt người dùng' : 'Đã từ chối người dùng');
      fetchUsers();
      fetchStats();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Không thể xử lý yêu cầu');
    }
  };

  const handleChangeRole = async (userId: string, newRole: string) => {
    try {
      await adminService.updateUserRole(userId, newRole);
      toast.success('Đã cập nhật vai trò người dùng');
      fetchUsers();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Không thể cập nhật vai trò');
    }
  };

  const handleSuspend = async (userId: string) => {
    const reason = prompt('Lý do tạm ngưng tài khoản:');
    if (!reason) return;

    try {
      await adminService.suspendUser(userId, reason);
      toast.success('Đã tạm ngưng tài khoản');
      fetchUsers();
      fetchStats();
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Không thể tạm ngưng tài khoản');
    }
  };

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-foreground">Quản lý người dùng</h1>
        <p className="text-muted-foreground mt-1">
          Quản lý tài khoản, phân quyền và phê duyệt người dùng
        </p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-card rounded-lg border border-border p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Tổng số</p>
              <h3 className="text-2xl font-bold text-foreground">{stats?.total_users || 0}</h3>
            </div>
            <Users className="w-8 h-8 text-blue-500" />
          </div>
        </div>

        <div className="bg-card rounded-lg border border-border p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Đang hoạt động</p>
              <h3 className="text-2xl font-bold text-green-600">{stats?.approved_users || 0}</h3>
            </div>
            <UserCheck className="w-8 h-8 text-green-500" />
          </div>
        </div>

        <div className="bg-card rounded-lg border border-border p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Chờ duyệt</p>
              <h3 className="text-2xl font-bold text-yellow-600">{stats?.pending_users || 0}</h3>
            </div>
            <Clock className="w-8 h-8 text-yellow-500" />
          </div>
        </div>

        <div className="bg-card rounded-lg border border-border p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Đã khóa</p>
              <h3 className="text-2xl font-bold text-red-600">{stats?.suspended_users || 0}</h3>
            </div>
            <UserX className="w-8 h-8 text-red-500" />
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-card rounded-lg border border-border p-4">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
            <input
              type="text"
              placeholder="Tìm kiếm theo email hoặc tên..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">Tất cả trạng thái</option>
            <option value="approved">Đã duyệt</option>
            <option value="pending">Chờ duyệt</option>
            <option value="suspended">Đã khóa</option>
            <option value="rejected">Đã từ chối</option>
          </select>

          {/* Role Filter */}
          <select
            value={roleFilter}
            onChange={(e) => setRoleFilter(e.target.value)}
            className="px-4 py-2 border border-border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">Tất cả vai trò</option>
            <option value="super_admin">Super Admin</option>
            <option value="admin">Admin</option>
            <option value="manager">Quản lý</option>
            <option value="analyst">Phân tích viên</option>
            <option value="viewer">Người xem</option>
          </select>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-card rounded-lg border border-border overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-muted">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Người dùng
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Thông tin
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Vai trò
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Trạng thái
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Ngày tạo
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-muted-foreground uppercase tracking-wider">
                  Hành động
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border">
              {loading ? (
                Array.from({ length: 5 }).map((_, i) => (
                  <tr key={i}>
                    <td className="px-6 py-4" colSpan={6}>
                      <div className="h-12 bg-muted rounded animate-pulse"></div>
                    </td>
                  </tr>
                ))
              ) : filteredUsers.length > 0 ? (
                filteredUsers.map((user) => (
                  <tr key={user.id} className="hover:bg-muted/50 transition-colors">
                    <td className="px-6 py-4">
                      <div>
                        <div className="font-medium text-foreground">{user.full_name}</div>
                        <div className="text-sm text-muted-foreground">{user.email}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm">
                        {user.department && (
                          <div className="text-muted-foreground">{user.department}</div>
                        )}
                        {user.position && (
                          <div className="text-muted-foreground text-xs">{user.position}</div>
                        )}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <select
                        value={user.role}
                        onChange={(e) => handleChangeRole(user.id, e.target.value)}
                        className={cn(
                          "px-3 py-1 rounded-full text-xs font-medium border-0",
                          roleColors[user.role] || 'bg-gray-100 text-gray-800'
                        )}
                        disabled={user.status !== 'approved'}
                      >
                        <option value="viewer">Người xem</option>
                        <option value="analyst">Phân tích viên</option>
                        <option value="manager">Quản lý</option>
                        <option value="admin">Admin</option>
                        <option value="super_admin">Super Admin</option>
                      </select>
                    </td>
                    <td className="px-6 py-4">
                      <span className={cn(
                        "px-3 py-1 rounded-full text-xs font-medium",
                        statusColors[user.status] || 'bg-gray-100 text-gray-800'
                      )}>
                        {user.status === 'approved' && 'Đã duyệt'}
                        {user.status === 'pending' && 'Chờ duyệt'}
                        {user.status === 'suspended' && 'Đã khóa'}
                        {user.status === 'rejected' && 'Từ chối'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-muted-foreground">
                      {new Date(user.created_at).toLocaleDateString('vi-VN')}
                    </td>
                    <td className="px-6 py-4 text-right">
                      <div className="flex items-center justify-end gap-2">
                        {user.status === 'pending' && (
                          <>
                            <button
                              onClick={() => handleApprove(user.id, true)}
                              className="p-2 text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                              title="Phê duyệt"
                            >
                              <CheckCircle className="w-4 h-4" />
                            </button>
                            <button
                              onClick={() => handleApprove(user.id, false)}
                              className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                              title="Từ chối"
                            >
                              <XCircle className="w-4 h-4" />
                            </button>
                          </>
                        )}
                        {user.status === 'approved' && (
                          <button
                            onClick={() => handleSuspend(user.id)}
                            className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Khóa tài khoản"
                          >
                            <UserX className="w-4 h-4" />
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center text-muted-foreground">
                    Không tìm thấy người dùng nào
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
