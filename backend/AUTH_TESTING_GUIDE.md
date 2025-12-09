# Authentication System - Testing Guide

## 📋 Tổng quan

Hệ thống xác thực đã được triển khai đầy đủ với:
- JWT Authentication (access_token + refresh_token)
- Role-based Access Control (super_admin, admin, manager, analyst, viewer)
- User approval workflow (pending → approved/rejected)
- MongoDB storage cho user data

## 🚀 Khởi động hệ thống

### 1. Backend (Docker)
```bash
cd /Users/vudangkhoa/Working/CityLens
docker-compose -f docker-compose.prod.yml up -d
```

Kiểm tra:
```bash
curl http://localhost:8000/health
# Response: {"status":"healthy","service":"citylens-backend","version":"0.3.0"}
```

### 2. Web Dashboard (Local)
```bash
cd /Users/vudangkhoa/Working/CityLens/web-dashboard
npm run dev
```

Truy cập: http://localhost:3000

## 👤 Tài khoản demo

### Super Admin (Đã duyệt)
- Email: `admin@citylens.com`
- Password: `Admin@2025`
- Role: `super_admin`
- Quyền: Quản lý toàn bộ hệ thống, duyệt user, gán role

### Manager (Đã duyệt)
- Email: `manager.gtvt@citylens.com`
- Password: `Manager@2025`
- Role: `manager`
- Quyền: Quản lý chức năng cụ thể

### Analyst (Đã duyệt)
- Email: `analyst.moitruong@citylens.com`
- Password: `Analyst@2025`
- Role: `analyst`
- Quyền: Xem và phân tích dữ liệu

### Pending User (Chờ duyệt)
- Email: `pending.user@citylens.com`
- Password: `User@2025`
- Role: `viewer`
- Status: `pending` - Cần admin duyệt mới đăng nhập được

## 🧪 Test Scenarios

### Test 1: Đăng nhập thành công
1. Truy cập http://localhost:3000
2. Nhập: `admin@citylens.com` / `Admin@2025`
3. Click "Đăng nhập"
4. ✅ Kết quả: Redirect đến `/dashboard` và hiển thị dashboard

### Test 2: Đăng nhập thất bại (sai password)
1. Truy cập http://localhost:3000/login
2. Nhập: `admin@citylens.com` / `wrongpassword`
3. Click "Đăng nhập"
4. ✅ Kết quả: Hiển thị lỗi "Email hoặc mật khẩu không đúng"

### Test 3: Đăng nhập với tài khoản chờ duyệt
1. Truy cập http://localhost:3000/login
2. Nhập: `pending.user@citylens.com` / `User@2025`
3. Click "Đăng nhập"
4. ✅ Kết quả: Hiển thị "Tài khoản đang ở trạng thái: pending. Vui lòng chờ admin duyệt."

### Test 4: Protected routes (chưa đăng nhập)
1. Truy cập http://localhost:3000/dashboard (chưa đăng nhập)
2. ✅ Kết quả: Tự động redirect đến `/login`

### Test 5: Đăng xuất
1. Đăng nhập thành công
2. Click nút "Đăng xuất" (trong dashboard)
3. ✅ Kết quả: Redirect về `/login`, xóa token khỏi localStorage

## 🔧 API Endpoints Test (Postman/curl)

### 1. Login API
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@citylens.com",
    "password": "Admin@2025"
  }'
```

Response:
```json
{
  "user": {
    "_id": "...",
    "email": "admin@citylens.com",
    "full_name": "Super Administrator",
    "role": "super_admin",
    "status": "approved"
  },
  "token": {
    "access_token": "eyJhbGci...",
    "refresh_token": "eyJhbGci...",
    "token_type": "bearer",
    "expires_in": 691200
  },
  "message": "Đăng nhập thành công"
}
```

### 2. Get Profile (with token)
```bash
TOKEN="<access_token từ login response>"

curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Get Pending Users (Admin only)
```bash
curl -X GET "http://localhost:8000/api/v1/admin/users/pending" \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Approve User (Admin only)
```bash
curl -X PUT "http://localhost:8000/api/v1/admin/users/<user_id>/approve" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "approved",
    "role": "analyst"
  }'
```

### 5. User Statistics
```bash
curl -X GET "http://localhost:8000/api/v1/admin/stats" \
  -H "Authorization: Bearer $TOKEN"
```

Response:
```json
{
  "total": 8,
  "pending": 1,
  "approved": 7,
  "rejected": 0,
  "suspended": 0
}
```

## 🐛 Troubleshooting

### Issue 1: "Internal Server Error" khi login
**Nguyên nhân**: Backend chưa khởi động hoặc MongoDB chưa connect

**Giải pháp**:
```bash
# Check backend logs
docker logs citylens-backend-prod --tail 50

# Restart backend
docker-compose -f docker-compose.prod.yml restart backend
```

### Issue 2: CORS error trên browser
**Nguyên nhân**: Frontend chạy ở port khác hoặc CORS chưa config

**Giải pháp**: Check `backend/app/core/config.py`:
```python
BACKEND_CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = [
    "http://localhost:3000",  # Web dashboard
    "http://localhost:8000",  # Backend docs
    "*"                       # Allow all (dev only)
]
```

### Issue 3: "Token không hợp lệ" ngay sau login
**Nguyên nhân**: Token expiration time settings

**Giải pháp**: Check `backend/app/core/config.py`:
```python
ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520  # 8 days
```

### Issue 4: Loading vô hạn sau khi click "Đăng nhập"
**Nguyên nhân**: API không response hoặc error không được handle

**Giải pháp**:
1. Mở DevTools (F12) → Network tab
2. Click "Đăng nhập"
3. Check request đến `/api/v1/auth/login`:
   - Status 200: Success → Check response data
   - Status 401: Wrong credentials
   - Status 500: Server error → Check backend logs
   - No request: Check API URL trong `.env.local`

## 📱 Frontend Configuration

File: `web-dashboard/.env.local`
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
```

## 🔐 Security Notes

1. **Password Requirements**:
   - Tối thiểu 8 ký tự
   - Phải có ít nhất 1 chữ số
   - Phải có ít nhất 1 chữ cái

2. **Token Expiration**:
   - Access Token: 8 days (691200 seconds)
   - Refresh Token: 30 days

3. **User Status Flow**:
   ```
   Register → pending → (Admin approve) → approved → Active
                      → (Admin reject)  → rejected
   ```

4. **Role Hierarchy**:
   ```
   super_admin (5) > admin (4) > manager (3) > analyst (2) > viewer (1)
   ```

## 📊 Current System Status

```bash
# Số lượng users hiện tại
Total: 8 users
- Approved: 7 users
- Pending: 1 user
- Rejected: 0 users
- Suspended: 0 users

# Demo accounts available:
✅ admin@citylens.com (super_admin, approved)
✅ manager.gtvt@citylens.com (manager, approved)
✅ analyst.moitruong@citylens.com (analyst, approved)
⏳ pending.user@citylens.com (viewer, pending)
```

## 🎯 Next Steps

1. ✅ Test đăng nhập trên web-dashboard
2. ✅ Test admin approval workflow
3. ⏳ Implement dashboard UI components
4. ⏳ Add user profile management page
5. ⏳ Add admin user management interface

---
**Last Updated**: December 9, 2025
**Version**: 1.0.0
