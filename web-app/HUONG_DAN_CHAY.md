# Hướng dẫn chạy Web App

## 📍 Vị trí folder
```
CityLens/
└── web-app/    ← Chạy app từ folder này
```

## 🚀 Các lệnh chạy app

### 1. Cài đặt dependencies (lần đầu hoặc sau khi cập nhật)
```powershell
cd web-app
npm install
```

### 2. Chạy app (Development mode)

**Cách 1: Dùng npm script (Khuyến nghị)**
```powershell
cd web-app
npm start
```

**Cách 2: Dùng script PowerShell**
```powershell
cd web-app
.\scripts\start.ps1
```

**Cách 3: Chạy trực tiếp với Expo**
```powershell
cd web-app
npx expo start
```

### 3. Chạy trên Web
Sau khi chạy `npm start`, nhấn phím `w` để mở trên web browser.

Hoặc chạy trực tiếp:
```powershell
cd web-app
npm run web
```

### 4. Setup tự động (cài đặt dependencies + tạo .env)
```powershell
cd web-app
npm run setup
```

Hoặc:
```powershell
cd web-app
.\scripts\setup.ps1
```

## ⚙️ Các lệnh khác

### Build cho production
```powershell
# Build cho web
npm run build:web

# Build cho Android
npm run build:android

# Build cho iOS
npm run build:ios
```

## 📝 Lưu ý

1. **Đảm bảo backend đang chạy** tại `http://localhost:8000`
2. **Kiểm tra file `.env`** có tồn tại và cấu hình đúng
3. **Port mặc định**: Expo web chạy trên `http://localhost:8081`

## 🔧 Troubleshooting

### Lỗi "Module not found"
```powershell
cd web-app
rm -r node_modules
npm install
```

### Lỗi "Port already in use"
```powershell
# Tìm và kill process đang dùng port 8081
netstat -ano | findstr :8081
taskkill /PID <PID> /F
```

### Clear cache
```powershell
cd web-app
npx expo start --clear
```

