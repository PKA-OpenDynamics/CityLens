# Netlify Environment Variables Setup

## 🎯 Chỉ cần 2 biến môi trường duy nhất!

Vào **Netlify Dashboard** → Site → **Site configuration** → **Environment variables** → **Add variable**

### Required Variables:

```bash
# 1. Backend API URL (BẮT BUỘC phải có /api/v1)
EXPO_PUBLIC_API_BASE_URL=https://your-tunnel.trycloudflare.com/api/v1

# 2. TomTom Maps API Key
TOMTOM_API_KEY=your_tomtom_api_key_here
```

## ✅ Tất cả endpoint tự động được tính từ EXPO_PUBLIC_API_BASE_URL:

- **Weather API**: `https://your-tunnel.trycloudflare.com` (bỏ `/api/v1`)
- **Reports API**: `https://your-tunnel.trycloudflare.com/api/v1/app` (thêm `/app`)
- **Auth API**: `https://your-tunnel.trycloudflare.com/api/v1/app` (thêm `/app`)
- **Alerts API**: `https://your-tunnel.trycloudflare.com/api/v1/alerts` (giữ nguyên + `/alerts`)

## 🔄 Khi thay đổi Cloudflare Tunnel URL:

1. Chỉ cần update **1 biến** `EXPO_PUBLIC_API_BASE_URL`
2. Trigger deploy lại: **Deploys** → **Trigger deploy** → **Clear cache and deploy**

## 📝 Ví dụ:

```bash
# Local development
EXPO_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1

# Production with Cloudflare Tunnel
EXPO_PUBLIC_API_BASE_URL=https://abc-def-ghi.trycloudflare.com/api/v1
```

## ⚠️ Lưu ý:

- URL **PHẢI** kết thúc bằng `/api/v1`
- Cloudflare free tunnel thay đổi mỗi lần restart
- Sau khi update biến môi trường, nhớ **Clear cache and deploy**
